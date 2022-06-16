
import asyncio
import argparse
from tabnanny import verbose
from PIL import Image
import cv2
import numpy as np
import requests
import os
from oscrypto import util as crypto_utils


from detection import dispatch as dispatch_detection, load_model as load_detection_model
from ocr import dispatch as dispatch_ocr, load_model as load_ocr_model
from textline_merge import dispatch as dispatch_textline_merge
from textblockdetector import dispatch as dispatch_ctd_detection
from textblockdetector.textblock import visualize_textblocks
from utils import convert_img

parser = argparse.ArgumentParser(description='Generate text bboxes given a image file')
parser.add_argument('--image', default='', type=str, help='Image file if using demo mode or Image folder name if using batch mode')
parser.add_argument('--image-dst', default='', type=str, help='Destination folder for translated images in batch mode')
parser.add_argument('--ocr-model', default='48px_ctc', type=str, help='OCR model to use, one of `32px`, `48px_ctc`')
parser.add_argument('--use-cuda', action='store_true', help='turn on/off cuda')
parser.add_argument('--translator', default='google', type=str, help='language translator')
parser.add_argument('--target-lang', default='ENG', type=str, help='destination language')
parser.add_argument('--use-ctd', action='store_true', help='use comic-text-detector for text detection')
parser.add_argument('--unclip-ratio', default=2.3, type=float, help='How much to extend text skeleton to form bounding box')
parser.add_argument('--box-threshold', default=0.7, type=float, help='threshold for bbox generation')
parser.add_argument('--text-threshold', default=0.5, type=float, help='threshold for text detections')

args = parser.parse_args()

async def infer(
	img,
	mode,
	nonce,
	options = None,
	task_id = '',
	dst_image_name = '',
	alpha_ch = None
	) :
	options = options or {}
	img_detect_size = 1536

	print(f' -- Detection resolution {img_detect_size}')
	detector = 'ctd' if args.use_ctd else 'default'
	if 'detector' in options :
		detector = options['detector']

	print(f' -- Detector using {detector}')
	render_text_direction_overwrite = 'v'

			
	print(f' -- Render text direction is {render_text_direction_overwrite or "auto"}')
	
	if detector == 'ctd' :
		mask, final_mask, textlines = await dispatch_ctd_detection(img, args.use_cuda)
		text_regions = textlines
	else:
		textlines, mask = await dispatch_detection(img, img_detect_size, args.use_cuda, args, verbose = True)


	if detector == 'ctd' :
		bboxes = visualize_textblocks(cv2.cvtColor(img,cv2.COLOR_BGR2RGB), textlines)
		cv2.imwrite(f'result/{task_id}/bboxes.png', bboxes)
		cv2.imwrite(f'result/{task_id}/mask_raw.png', mask)
		cv2.imwrite(f'result/{task_id}/mask_final.png', final_mask)
	else:
		img_bbox_raw = np.copy(img)
		for txtln in textlines :
			cv2.polylines(img_bbox_raw, [txtln.pts], True, color = (255, 0, 0), thickness = 2)


	textlines = await dispatch_ocr(img, textlines, args.use_cuda, args, model_name = args.ocr_model)

	textPositions = []
	if detector == 'default' :
		text_regions, textlines = await dispatch_textline_merge(textlines, img.shape[1], img.shape[0], True)
		img_bbox = np.copy(img)
		for region in text_regions :
			for idx in region.textline_indices :
				txtln = textlines[idx]
				if txtln.pts[0][1] >= 12: # not take if the text is too high (this is used to sshow the title with the page in many novels)
					textPositions.append((txtln.text, txtln.pts[0][0]))
				cv2.polylines(img_bbox, [txtln.pts], True, color = (255, 0, 0), thickness = 2)
			img_bbox = cv2.polylines(img_bbox, [region.pts], True, color = (0, 0, 255), thickness = 2)

		cv2.imwrite(f'{dst_image_name}.png', cv2.cvtColor(img_bbox, cv2.COLOR_RGB2BGR))

	sortedTextPositions = sorted(textPositions, key=lambda tup: tup[1], reverse=True)

	translated_sentences = None

	print(' -- Translating text')

	from translators import dispatch as run_translation

	with open(f'{dst}/result.txt', 'a+', encoding="utf-8") as f:
		if detector == 'ctd' :
			for setences in [r.get_text() for r in text_regions]:
				print(setences + '\n')
		else:
			translated_sentences = await run_translation(args.translator, 'auto', args.target_lang, [setences[0] for setences in sortedTextPositions])
			print("TRANSLATED : ")
			print(translated_sentences)
			for x in translated_sentences:
				f.write(x + '\n\n')

	f.close()

	# ETRE SUR QUE TT S'ECRIT BIEN ET FAIRE EN SORTE QU'IL PREND PARAGRAPHE ET NON LIGNE c facile genre juste replace par textline.text ou autre
	# PRENDRE LES IMAGES ORDRE CROISSANT
	# TRANSLATION + RAPIDE 


async def infer_safe(
	img,
	mode,
	nonce,
	options = None,
	task_id = '',
	dst_image_name = '',
	alpha_ch = None
	) :
	try :
		return await infer(
			img,
			mode,
			nonce,
			options,
			task_id,
			dst_image_name,
			alpha_ch
		)
	except :
		import traceback
		traceback.print_exc()
		update_state(task_id, nonce, 'error')

def replace_prefix(s: str, old: str, new: str) :
	if s.startswith(old) :
		s = new + s[len(old):]
	return s

# https://stackoverflow.com/questions/6670029/can-i-force-os-walk-to-visit-directories-in-alphabetical-order
import re
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

async def main(mode = 'demo') :
	print(' -- Loading models')

	with open('alphabet-all-v5.txt', 'r', encoding = 'utf-8') as fp :
		dictionary = [s[:-1] for s in fp.readlines()]
	load_ocr_model(dictionary, args.use_cuda, args.ocr_model)
	from textblockdetector import load_model as load_ctd_model
	load_ctd_model(args.use_cuda)
	load_detection_model(args.use_cuda)

	src = os.path.abspath(args.image)
	if src[-1] == '\\' or src[-1] == '/' :
		src = src[:-1]
	global dst
	dst = args.image_dst or src + '-translated'
	if os.path.exists(dst) and not os.path.isdir(dst) :
		print(f'Destination `{dst}` already exists and is not a directory! Please specify another directory.')
		return
	if os.path.exists(dst) and os.listdir(dst) :
		print(f'Destination directory `{dst}` already exists! Please specify another directory.')
		return
	print('Processing image in source directory')
	files = []
	for root, subdirs, files in os.walk(src) :
		dst_root = replace_prefix(root, src, dst)
		os.makedirs(dst_root, exist_ok = True)
		for f in sorted(files, key=natural_keys) :
			if f.lower() == '.thumb' :
				continue
			filename = os.path.join(root, f)
			try :
				img, alpha_ch = convert_img(Image.open(filename))
				img = np.array(img)
				if img is None :
					continue
			except Exception :
				pass
			try :
				dst_filename = replace_prefix(filename, src, dst)
				print('Processing', filename, '->', dst_filename)
				await infer(img, 'demo', '', dst_image_name = dst_filename, alpha_ch = alpha_ch)
			except Exception :
				import traceback
				traceback.print_exc()
				pass

if __name__ == '__main__':
	print(args)
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main("batch"))

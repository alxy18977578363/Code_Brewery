import re
from pathlib import Path

PUNCTUATION = set(list('，。！？；；,.;:!:?、"”“’‘—…'))

def is_punct_char(ch: str) -> bool:
	return ch in PUNCTUATION

def word_to_labelled_chars(word: str):
	"""Convert a word (string of chars) to list of (char,label).

	Labels: S (single), B (begin), M (middle), E (end)
	"""
	chars = list(word)
	n = len(chars)
	if n == 0:
		return []
	if n == 1:
		return [(chars[0], 'S')]
	out = []
	for i, ch in enumerate(chars):
		if i == 0:
			lab = 'B'
		elif i == n - 1:
			lab = 'E'
		else:
			lab = 'M'
		out.append((ch, lab))
	return out

def process_msr_training(input_path, output_path):
	"""Read msr training file and write processed char-level labeled data.

	Rules implemented:
	- Strip leading/trailing quotation marks from tokens and lines.
	- Use existing whitespace tokenization as words; convert each word into B/M/E/S labels per character.
	- Treat punctuation (comma、period、question/exclamation etc.) as sentence boundaries — do not emit punctuation characters.
	- Output format: one char and its label per line, sentences separated by a blank line (utf-8 encoded).
	"""
	input_path = Path(input_path)
	output_path = Path(output_path)
	quote_chars = '"“”‘’'  # to strip from tokens

	sep_regex = re.compile(r'([，。！？；,.;:!:?、\"”“’‘—…])')

	with input_path.open('r', encoding='utf-8', errors='ignore') as fin, \
			output_path.open('w', encoding='utf-8') as fout:
		for raw_line in fin:
			line = raw_line.strip()
			if not line:
				continue
			# remove leading quote characters if line starts with them
			while line and line[0] in quote_chars:
				line = line[1:]
			# also remove trailing quote
			while line and line[-1] in quote_chars:
				line = line[:-1]

			# split by whitespace to get words (msr training uses spaces between words)
			tokens = [t for t in re.split(r'\s+', line) if t]
			sentence_chars = []  # accumulate (char,label) for current sentence

			for token in tokens:
				# strip quotes around token
				token = token.strip(quote_chars)
				if not token:
					continue

				# split token by punctuation, keep separators
				parts = sep_regex.split(token)
				for part in parts:
					if not part:
						continue
					if sep_regex.fullmatch(part):
						# punctuation — finalize current sentence
						if sentence_chars:
							for ch, lab in sentence_chars:
								fout.write(f"{ch} {lab}\n")
							fout.write("\n")
							sentence_chars = []
						# drop punctuation (do not emit)
						continue
					# normal word segment -> produce labels
					labelled = word_to_labelled_chars(part)
					sentence_chars.extend(labelled)

			# end of line: flush remaining sentence
			if sentence_chars:
				for ch, lab in sentence_chars:
					fout.write(f"{ch} {lab}\n")
				fout.write("\n")



def load_labelled_sentences(processed_path):
	"""Load processed file and return list of (chars_list, labels_list).

	Expects file format: each non-empty line contains `char label` and
	sentences separated by a blank line.
	"""
	processed_path = Path(processed_path)
	sentences = []
	chars = []
	labels = []
	with processed_path.open('r', encoding='utf-8', errors='ignore') as fin:
		for raw in fin:
			line = raw.strip()
			if not line:
				if chars:
					sentences.append((chars, labels))
					chars = []
					labels = []
				continue
			parts = line.split()
			if len(parts) >= 2:
				ch = parts[0]
				lab = parts[-1]
				chars.append(ch)
				labels.append(lab)
	if chars:
		sentences.append((chars, labels))
	return sentences


def prepare_dataset(processed_path=None, raw_path=None):
	base = Path(__file__).resolve().parents[1]
	if raw_path is None:
		raw_path = base / 'data' / 'train' / 'msr_training.utf8'
	if processed_path is None:
		processed_path = base / 'data' / 'train' / 'msr_training_processed.utf8'

	processed_path = Path(processed_path)
	if not processed_path.exists():
		process_msr_training(raw_path, processed_path)

	sentences = load_labelled_sentences(processed_path)
	return sentences

####### 这个main给自己调用，上面的prepare_dataset才是给外部调用的接口，main里调用了process_msr_training来生成processed文件 #######
def main():
	base = Path(__file__).resolve().parents[1]
	in_file = base / 'data' / 'train' / 'msr_training.utf8'
	out_file = base / 'data' / 'train' / 'msr_training_processed.utf8'
	process_msr_training(in_file, out_file)
	print(f'Wrote processed training data to {out_file}')


if __name__ == '__main__':
	main()

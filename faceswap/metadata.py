METADATA =\
{
	'name': 'FaceSwap',
	'description': 'Next generation face swapper and enhancer',
	'version': '1.0.0',
	'license': 'MIT',
	'author': 'Gilad Leef',
	'url': 'https://github.com/giladleef/faceswap'
}


def get(key : str) -> str:
	return METADATA[key]

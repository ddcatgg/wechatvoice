import os
import shutil


for root, dirs, files in os.walk('.'):
	for file in files:
		if file.endswith('.amr'):
			filename = os.path.join(root, file)
			shutil.move(filename, './' + file)

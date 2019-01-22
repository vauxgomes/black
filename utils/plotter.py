#!/usr/bin/python

# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com

import json
import argparse

#
AMP = 1.3
PREVIEW = False
LEGEND = False
TOTAL_RANGE = False
SHOW_MAX = False
NORM = False
EXT = ".png"

#
LINESTYLE = ['-', '--', '-.', ':']

#
COMMENT = "#"
META = "@"
ALGSEP = "~" # Algorithm separator

# Argument parsing method
def arg_parsing():
	parser = argparse.ArgumentParser(description="Plooter for boost_lac.py output")
	parser.add_argument("-f", "-F", nargs="*", help="Files.", required=True)
	
	parser.add_argument("-l", help="Show legend", action="store_false")
	parser.add_argument("-p", help="Preview image and avoid saving", action="store_true")
	parser.add_argument("-t", help="Total range", action="store_true")
	parser.add_argument("-m", help="Show maximum values", action="store_true")
	parser.add_argument("-e", help="Save in EPS format", action="store_true")

	parser.add_argument("-w", help="Print lines and avoiding creating pictures.", action="store_true")
	parser.add_argument("-g", help="Print lines in gnuplot friendly format.", action="store_true")
	parser.add_argument("-r", help="Signal for processing the file(s) (Default: True)", action="store_false")

	parser.add_argument("--show", nargs="*", help="Closed list of lines it must draw.", type=int)
	parser.add_argument("--skip", nargs="*", help="Closed list of lines it mustn't draw.", type=int)
	parser.add_argument("--vline", nargs="*", help="Vertical lines", type=int)

	parser.add_argument("--norm", help="Normalize <@> tag", action="store_true")
	parser.add_argument("--model", nargs=1, help="<file_name>.<model>.png")
	parser.add_argument("--title", nargs=1, help="Set the figure's name")

	return parser.parse_args()

#
def read_raw_curves(file):
	fold = {}
	counter = {}
	
	ids = {}
	acc = {}
	fold_count = 0
	unprocessed = False

	metas = {}
	meta_count = {}

	#
	def process_fold(fold, acc):
		for alg in fold:
			# Safety
			if alg not in acc: acc[alg] = [0.0]*len(fold[alg])

			for i in range(len(fold[alg])):
				acc[alg][i] += float(fold[alg][i])/counter[alg][i]

	#
	with open(file, "r") as handler:
		for row in handler:
			if row.startswith(COMMENT) or row == "\n":
				pass
				# if unprocessed:
				# 	# Processing current fold
				# 	process_fold(fold, acc)

				# 	fold = {}
				# 	counter = {}
				# 	unprocessed = False

				# 	fold_count += 1
			elif row.startswith(META):
				row = row.split()
				label = row[1]
				row = row[2:]

				if label not in metas:
					metas[label] = [0]*len(row)
					meta_count[label] = 0

				for i in range(len(row)):
					metas[label][i] += float(row[i])

				meta_count[label] += 1
			else:
				unprocessed = True

				row = row.strip()
				row = row.split(ALGSEP)
				ref = row[0].strip()

				for i in range(1, len(row)):
					line = row[i].split()
					alg = line[0]

					# Safety
					if alg not in ids: ids[alg] = len(ids)
					if alg not in fold:
						fold[alg] = [0]*(len(line) - 1)
						counter[alg] = [0]*(len(line) - 1)

					# Safety
					while len(fold[alg]) < len(line) - 1:
						fold[alg].append(0)
						counter[alg].append(0)

					for j in range(1, len(line)):
						if line[j] == ref:
							fold[alg][j-1] += 1

						counter[alg][j-1] += 1

	# Safety
	if unprocessed:
		process_fold(fold, acc)
		fold_count += 1

	# Preparing final format
	output = {}
	for alg in acc:
		for i in range(len(acc[alg])):
			acc[alg][i] /= float(fold_count)

		# Saving alg
		output[ids[alg]] = {"name": alg, "points": acc[alg]}

	# META TAG
	for label in metas:
		values = [v/meta_count[label] for v in metas[label]]

		# For normalization purposes
		if (NORM):
			max_ = max(values)
			min_ = min(values)
			diff = max_ - min_
			
			for i in range(len(values)):
				values[i] = (values[i] - min_)/diff

		output[len(output)] = {"name": label, "points": values}

	return output

#
def read_processed_curves(file):
	lines = {}	
	with open(file, "r") as handler:
		for row in handler:
			#
			row = row.strip().split()
			if len(row) == 0: continue

			#
			lines[len(lines)] = {
				"name": row[0],
				"points": [float(row[i]) for i in xrange(1, len(row))]
			}

			#
			if (NORM):
				line = len(lines) - 1
				max_ = max(lines[line]["points"])
				min_ = min(lines[line]["points"])
				range_ = max_ - min_

				if range_ > 0:
					for i in xrange(len(lines[line]["points"])):
						lines[line]["points"][i] = (lines[line]["points"][i] - min_)/range_


	return lines

#
def save_lines(lines, gnuplot=False, model=None, show=None, skip=None):
	if model is None: model = ""
	
	# Lines to show
	if show is None: show = range(0, len(lines))
	if skip is not None:
		for i in skip:
			if i in show:
				show.remove(i)

	if not gnuplot:
		for line in show:
			if line not in lines: continue

			#
			print lines[line]["name"].replace(ALGSEP, "") + model,
			
			#
			if not SHOW_MAX:
				for i in lines[line]["points"]:
					print i,

				print ""
			else:
				max_ = max(lines[line]["points"]) 
				print max_, lines[line]["points"].index(max_) + 1
	else:
		pass

def plot_figure(lines, figname, title=None, show=None, skip=None, model=None, vlines=None):
	# Adjusting name
	index = figname.rfind("/")
	if index > 0: title = figname[index + 1:]
	elif title == None: title = figname
	#
	index = title.find(".")
	if index > 0: title = title[:index]

	# Lines to show
	if show is None: show = range(0, len(lines))
	if skip is not None:
		for i in skip:
			if i in show:
				show.remove(i)

	vmax = {}
	MIN_ROUNDS = 1
	MAX_ROUNDS = max(2, max([len(lines[line]["points"]) for line in show]))

	# Plot Settings
	W, H = 12 * AMP, 7.2 * AMP
	fig = plt.figure(figsize=(W, H))
	
	if TOTAL_RANGE:
		boundaries = {
			'axis':[MIN_ROUNDS - 1, MAX_ROUNDS + 1, -.01, 1.01],
			'yticks': [value / 40.0 for value in range(0, 40 + 1, 2)]
		}
	else:
		boundaries = {
			'axis':[MIN_ROUNDS - 1, MAX_ROUNDS + 1, 0.5, 1.001],
			'yticks': [value / 40.0 for value in range(20, 40 + 1, 2)]
		}

	plt.axis(boundaries['axis'])
	plt.yticks(boundaries['yticks'])

	step = max(int(MAX_ROUNDS / 20.0), 5)
	xticks = range(MIN_ROUNDS, MAX_ROUNDS + 1, step)
	# xticks = range(1, 11)

	plt.xticks(xticks) #, rotation='vertical')
	plt.grid(True)

	plt.xlabel('N. Regras')
	plt.ylabel('Erro Normalizado')
	
	plt.xlabel('Complexidade')
	plt.ylabel(r'Acuracia Normalizada')

	plt.xlabel('N. Regras')
	plt.ylabel('Acuracia')

	plt.title(title)

	# plt.annotate("test", xy=(10, 0.5))

	# X array
	X = range(MIN_ROUNDS, MAX_ROUNDS + 1)

	# Plotting lines
	for line in show:
		# Safety
		if line not in show: continue

		label = lines[line]["name"].replace(ALGSEP, "")
		
		# Y array
		Y = lines[line]["points"]
		if len(Y) == 1: Y = Y * MAX_ROUNDS
		else:
			while len(X) > len(Y):
				Y.append(Y[-1])

		# Maximum value
		if SHOW_MAX:
			max_ = max(Y)
			index = Y.index(max_)

			if max_ in vmax: vmax[max_].append((label, index))
			else: vmax[max_] = [(label, index)]

		# Plotting
		plt.plot(X, Y, label=label, linewidth=3, linestyle=LINESTYLE[0], marker=",")#, color="black")

	#
	if SHOW_MAX:
		#
		ymin = boundaries['axis'][2]
		ymax = boundaries['axis'][3]

		height, dec = 1.0, (0.03 if TOTAL_RANGE else 0.015)
		list_ = [(max_, index, label) for max_ in vmax for label, index in vmax[max_]]
		list_ = sorted(list_, key=lambda x: (x[0], x[1]), reverse=True)

		#
		for max_, index, label in list_:
			height -= dec
			plt.plot((index+1, index+1), (ymin, ymax), 'k-', linestyle=LINESTYLE[2])
			plt.annotate(label+": "+str(max_)[:6], xy=(index+2, height))

	# Activating legend
	if LEGEND: plt.legend(loc='lower right', fancybox=True, )#ncol=4)

	# Showing or Saving
	if PREVIEW: plt.show()
	else:
		plt.savefig(figname + EXT)
		print figname + EXT

	plt.close()

# MAIN
if __name__ == "__main__":
	# Arguments
	args = arg_parsing()

	# Settings
	PREVIEW = args.p
	LEGEND = args.l
	TOTAL_RANGE = args.t
	SHOW_MAX = args.m
	NORM = args.norm

	#
	import matplotlib 

	if args.e:
		# EPS
		matplotlib.use('Agg') # EPS
		EXT = ".eps"

	import matplotlib.pyplot as plt

	#
	if PREVIEW: AMP = 1.15
	if args.model is not None: args.model = args.model[0]
	if args.title is not None: args.title = args.title[0]

	for file in args.f:
		# Safety
		if file.endswith(".png") or file.endswith(".py") \
			or file.endswith(".tar") or file.endswith(".eps"):
			# print "WARNING: File", file, "not processed"
			continue

		# Figure name
		if PREVIEW == False and args.model != None: figname = file + "." + args.model
		else: figname = file # file[:file.find(".")]

		# Reading
		if args.r: lines = read_raw_curves(file)
		else: lines = read_processed_curves(file)

		# Saving processed file
		if args.w or args.g:
			save_lines(lines, args.g, args.model, args.show, args.skip)
			continue

		# Plot figure
		plot_figure(lines, figname, args.title, args.show, args.skip, args.model, args.vline)
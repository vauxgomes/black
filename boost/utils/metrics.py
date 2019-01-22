# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
Many rule metrics

References
----------
[1] L Geng, HJ Hamilton. Interestingness measures for
data mining: A survey - ACM Computing Surveys (CSUR), 2006

'''

# Confidence
def confidence(rule, classes):
	coverage = sum([len(rule.supp[class_]) for class_ in classes])	
	return {class_: len(rule.supp[class_]) / float(coverage) for class_ in classes}

# Support
def support(rule, classes, tsize): # tsize = size of the whole projection
	return {class_: len(rule.supp[class_]) / float(tsize) for class_ in classes} 

# Lift
def lift(rule, classes, tsupp):
	supp = sum([len(rule.supp[class_]) for class_ in classes])
	return {class_: len(rule.supp[class_]) / float(supp * tsupp[class_]) for class_ in classes}

# Conviction
def conviction(rule, classes, tsupp): # tsupp[Y] = supp(Y)
	conv = {}
	for class_ in classes:
		if rule.confidence[class_] == 1:
			conv[class_] = 0
		else:
			conv[class_] = (1.0 - tsupp[class_]) / (1 - rule.confidence[class_])

	return conv
# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module sets up a classification model for
Lazy Associative Classifer (LAC)

References
----------
[1] Adriano Veloso and Wagner Meira Jr, Demand-driven
associative classification. Spring, 2011.

'''

# Imports
import utils.metrics as metrics
from core.ruleclassifier import RuleClassifier

# Lazy Associative Classification
def lac(itemsets, classes):
	model = []
	
	for it in itemsets:
		conf = metrics.confidence(it, classes)
		
		for class_ in classes:
			model.append((RuleClassifier(it, class_, conf[class_]), 1.0))
		
	return model

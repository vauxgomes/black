# Author: Vaux Gomes
# Contact: vauxgomes@gmail.com
# Version: 0.1

'''

Description
-----------
This module sets up a classification model for
the ZERO algorithm, which has only the default rule.

'''

# Imports
from core.itemset import Itemset
from core.ruleclassifier import RuleClassifier

# ZERO
def zero():		
	return [(RuleClassifier(Itemset(-1, None, None, default=True), None, 1.0),1.0)]

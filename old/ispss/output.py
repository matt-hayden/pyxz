#!env python

### from: ExportToExcel.py

import os.path

import SpssClient

import ispss
"""
Example for reference:

def spss_set_output_Excel(filename, sheetname="SPSS output"):
	SpssClient.StartClient()
	OutputDoc = SpssClient.GetDesignatedOutputDoc()
	OutputDoc.ClearSelection()
	#
	OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelOperationOptions,
							   "CreateWorkbook")
	OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelSheetNames,
							   sheetname)
	OutputItems = OutputDoc.GetOutputItems()
	# Select all interesting output
	for index in range(OutputItems.Size()):
		OutputItem = OutputItems.GetItemAt(index)
		if (OutputItem.GetType() == SpssClient.OutputItemType.HEAD and
			"Descriptives" in OutputItem.GetDescription()):
			OutputItem.SetSelected(True)
	try:
		OutputDoc.ExportDocument(SpssClient.SpssExportSubset.SpssSelected,
								 os.path.abspath(filename),
	SpssClient.DocExportFormat.SpssFormatXls)
	except Exception as e:
		print e
	OutputDoc.ClearSelection()
### http://pic.dhe.ibm.com/infocenter/spssstat/v21r0m0/index.jsp?topic=%2Fcom.ibm.spss.statistics.python.help%2Fpython_scripting_spssoutputdoc_setoutputoptions.htm
for index in range(OutputItems.Size()):
    OutputItem = OutputItems.GetItemAt(index)
    if OutputItem.GetType() == SpssClient.OutputItemType.PIVOT:
        OutputItem.SetSelected(True)
"""
def save_Excel(filename,
			   sheetname="SPSS output",
			   mode='a',
			   subSet=SpssClient.SpssExportSubset.SpssVisible,
			   startClient=True):
	"""
	Write the active output document as an Excel file.
	"""
	if startClient: SpssClient.StartClient()
	OutputDoc = SpssClient.GetDesignatedOutputDoc()
	#
	afilename = filename if os.path.isabs(filename) else os.path.join(ispss.get_cwd(), filename)
	ext = os.path.splitext(afilename)[-1].upper()
	#
	if ext in ['.XLS']:
		format = SpssClient.DocExportFormat.SpssFormatXls
	#elif ext in ['.XLSX']:
	#
	if isinstance(subSet, basestring):
		if subSet.startswith('select'):
			subSet = SpssClient.SpssExportSubset.SpssSelected
		elif subSet == 'visible':
			subSet = SpssClient.SpssExportSubset.SpssVisible
		elif subSet == 'all':
			subSet = SpssClient.SpssExportSubset.SpssAll
	if mode == 'a':
		OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelOperationOptions,
								   "CreateWorksheet")
	elif mode == 'w':
		OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelOperationOptions,
								   "CreateWorkbook")
	OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelSheetNames,
							   sheetname)
	try:
		OutputDoc.ExportDocument(subSet, afilename, format)
		OutputDoc.SetPromptToSave(False)
		return afilename
	except Exception as e:
		print e
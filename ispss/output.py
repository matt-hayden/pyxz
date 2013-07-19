#!env python

### from: ExportToExcel.py

import os.path

import SpssClient

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
			   subSet=SpssClient.SpssExportSubset.SpssVisible,
			   startClient=True):
	"""
	Write the active output document as an Excel file.
	"""
	if startClient: SpssClient.StartClient()
	OutputDoc = SpssClient.GetDesignatedOutputDoc()
	OutputDoc.ClearSelection()
	#
	OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelOperationOptions,
							   "CreateWorkbook")
	OutputDoc.SetOutputOptions(SpssClient.DocExportOption.ExcelSheetNames,
							   sheetname)
	try:
		OutputDoc.ExportDocument(subSet,
								 filename if os.path.isabs(filename) else os.path.join(cwd, filename),
								 SpssClient.DocExportFormat.SpssFormatXls)
		OutputDoc.SetPromptToSave(False)
	except Exception as e:
		print e
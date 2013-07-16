#ExportToExcel.py
import os.path

import SpssClient

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
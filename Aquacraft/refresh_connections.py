#
import os.path
import time

from win32com.client import Dispatch

from Aquacraft.mkodc import *

table_name_by_label = { 'Access_tblSummary': 'tblSummary',
                        'Access_tblFaucetDurationHistogram': 'tblFaucetDurationHistogram',
                        'Access_tblFaucetVolumeHistogram': 'tblFaucetVolumeHistogram',
                        'Access_tblShowerDurationHistogram': 'tblShowerDurationHistogram',
                        'Access_tblShowerVolumeHistogram': 'tblShowerVolumeHistogram',
                        'Access_tblToiletFlushVolume': 'tblToiletFlushVolume'
                        }

def update_Excel_connections(spreadsheet, database, table_name_by_label=table_name_by_label, quit=True, excel=None):
    database_filename = os.path.abspath(database)
    database_dirname, database_basename = os.path.split(database_filename)
    database_name, ext = os.path.splitext(database_basename)
    assert os.path.exists(database_filename)

    spreadsheet_filename = os.path.abspath(spreadsheet)
    spreadsheet_dirname, spreadsheet_basename = os.path.split(spreadsheet_filename)
    spreadsheet_name, ext = os.path.splitext(spreadsheet_basename)
    excel = excel or Dispatch("Excel.Application")
    excel.Visible = True
    print "Loading", spreadsheet_filename
    excel.Workbooks.Open(spreadsheet_filename)

    labels = [ conn.Name for conn in excel.ActiveWorkbook.Connections ]
    for label in labels:
        if label in table_name_by_label:
            tn = table_name_by_label[label]
            print label, "found"
            odc_filename = local.sanitize.path_sanitize(database_name+'_'+tn+'.ODC')
            odc_path = os.path.join(spreadsheet_dirname, odc_filename)
            print make_odc(database_filename, odc_path, name=label, table=tn), "written"
            excel.ActiveWorkbook.Connections[label].Delete()
            excel.ActiveWorkbook.Connections.AddFromFile(odc_path)
    if labels:
        excel.ActiveWorkbook.RefreshAll()
        time.sleep(len(labels))
        print spreadsheet_filename, "updated"
        excel.ActiveWorkbook.Save()
        time.sleep(5)
        print spreadsheet_filename, "saved"
    if quit: excel.Quit()
    del excel
if __name__ == '__main__':
#    update_Excel_connections(r'foo.xlsx', r'Z:\Projects\Abu Dhabi\Monitoring Period 2\TW Files_MP2\stats\AbuDhabi MP2 stats.mdb')
    update_Excel_connections(r'foo.xlsx', r'Z:\Projects\Abu Dhabi\Monitoring Period 1\TW Files_MP1\stats\AbuDhabi MP1 stats (update 2013-12-06).mdb')
from flow_types.isk import IskType
from flow_types.iskstatus import IskstatusType
from flow_types.application import ApplicationType
from flow_types.downloadIspListByTalon import DownloadIspListByTalonType
from flow_types.downloadIspListPismo import DownloadIskListPismoType
from flow_types.sp import SpType
from flow_types.moveBy2Subfolder import MoveBy2SubfolderType
from flow_types.moveOneFile import MoveOneFileType
from flow_types.generateFilesByTemplate import GenerateFilesByTemplateType
from flow_types.moveTalon import MoveTalonType
from flow_types.renameIsk import RenameIskType
from flow_types.renamePdf import RenamePdfType
from flow_types.getExcelFromPdf import GetExcelFromPdfType
from flow_types.converter import ConverterType

types = {
    1: IskType,
    2: IskstatusType,
    3: ApplicationType,
    4: SpType,
    5: DownloadIspListByTalonType,
    6: DownloadIskListPismoType,
    7: GenerateFilesByTemplateType,
    8: MoveBy2SubfolderType,
    9: MoveOneFileType,
    10: MoveTalonType,
    11: RenameIskType,
    12: RenamePdfType,
    13: GetExcelFromPdfType,
    14: ConverterType
}

excelTypes = {
    1: IskType,
    2: IskstatusType,
    3: ApplicationType,
    4: SpType,
    5: DownloadIspListByTalonType,
    6: GenerateFilesByTemplateType
}

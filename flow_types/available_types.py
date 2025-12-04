from flow_types.isk import IskType
from flow_types.iskstatus import IskstatusType
from flow_types.application import ApplicationType
from flow_types.downloadIspListByTalon import DownloadIspListByTalonType
from flow_types.downloadIspListPismo import DownloadIskListPismoType
from flow_types.sp import SpType
from flow_types.moveBy2Subfolder import MoveBy2SubfolderType
from flow_types.moveOneFile import MoveOneFileType

types = {
    1: IskType,
    2: IskstatusType,
    3: ApplicationType,
    4: SpType,
    5: DownloadIspListByTalonType,
    6: DownloadIskListPismoType,
    7: MoveBy2SubfolderType,
    8: MoveOneFileType
}

excelTypes = {
    1: IskType,
    2: IskstatusType,
    3: ApplicationType,
    4: SpType,
    5: DownloadIspListByTalonType
}

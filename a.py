# import time
# from common.input_text import textByLabel
# from common.button import clickByText
# from common.input_upload import uploadFile, uploadAllFilesInDirectory
# from common.read_pdf import read
# from browser.browser import Browser
# import re
# import os
# from pathlib import Path

# from globals import RETRY_COUNT

# def parse(text):
#     result = {}

#     zayav_pattern = r"О вынесении судебного приказа\s*(.*?)(?=ПРОСИМ\s+СУД:)"
#     zayav_match = re.search(zayav_pattern, text, re.S | re.I)
#     if zayav_match:
#         result["zayavlenie"] = zayav_match.group(1).strip()

#     prosim_pattern = r"(ПРОСИМ\s+СУД:.*?)(?=\s*Приложение)"
#     prosim_match = re.search(prosim_pattern, text, re.S | re.I)
#     if prosim_match:
#         result["prosim"] = prosim_match.group(1).strip()

#     return result


# a = Path('Медиации подача/1/1.pdf')
# parsed = parse(read(str(a.resolve())))
# print(parsed['prosim'])

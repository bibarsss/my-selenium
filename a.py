# import re
# from common.read_pdf import read
# from pathlib import Path
# def parse_claim(text: str):
#     result = {}
#     contract_pattern = r"(\d{2}\.\d{2}\.\d{4} года.*?)(?=На основании изложенного)"
#     contract_match = re.search(contract_pattern, text, re.S | re.I)
#     if contract_match:
#         result["contract_block"] = contract_match.group(1).strip()
#     prosim_pattern = r"(На основании изложенного.*?)(?:ПРИЛОЖЕНИЕ|$)"
#     prosim_match = re.search(prosim_pattern, text, re.S | re.I)
#     if prosim_match:
#         result["prosim_block"] = prosim_match.group(1).strip()
#     return result
# p = Path('isk.pdf')
# parsed = parse_claim(read(str(p.resolve())))
# for i in parsed:
#     print('0000000000000000000000000000000000000')
#     print(parsed[i])
#     print('0000000000000000000000000000000000000')

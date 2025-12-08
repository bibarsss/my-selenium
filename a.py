
# import requests

# import os

# url = "https://office.sud.kz/letter/attachDownload?uid=2EF29E3E242948A2A59C9F71AD4D9FEA"

# # Folder where you want to save the file
# folder = "downloads"
# os.makedirs(folder, exist_ok=True)  # create folder if it doesn't exist

# # Full path including filename
# output_file = os.path.join(folder, "downloaded_file.pdf")

# response = requests.get(url, verify=False)  # ignore SSL verification
# response.raise_for_status()

# with open(output_file, "wb") as f:
#     f.write(response.content)

# print(f"File saved as {output_file}")

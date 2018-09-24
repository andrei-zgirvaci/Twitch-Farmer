
# Twitch Follower Bot Farmer (Twitch-Farmer)

Twitch Farmer is a bot that helps you to get more followers.
Often when new twitch streamers start, they come to realize that their content does not get the quality it deserves. Due to the nature of Twitch, to sort the channels based on the follower count, new streamers do not get a chance at all to present their content. Twitch Farmer presents the solution, by offering all the needed features, to boost your channel in the ranks, while maintaining a natural look to other real viewers.

WRITTEN BY: Andrei Zgirvaci

CONTRIBUTE: Contributions are always welcome!

*If you can, please take a minute to star this repo and follow me, It will be much appreciated!!!*

---

## Requirements

* **python** version **3.7.0** installed

## Installation

```bash
git clone https://github.com/MD3XTER/Twitch-Farmer.git

cd Twitch-Farmer

pip install selenium pandas

python3 twitch_farmer.py
```

## Usage

In order for the bot to run, you need to add at least one account to the accounts.csv file located in the _data_ folder.

You only need to specify the **username** and **password**, the **following_channel** and **used_proxy** columns are filled by the bot for _log_ purposes.

|**username**|**password**|**following_channel**|**used_proxy**|
|---|---|---|---|
|_root_|_toor_|||

---

Besides accounts.csv file you also need too specify the proxies in the  proxies.csv file located in the _data_ folder.

You only need to specify the **proxy**. The **status** column is filled by the bot for _log_ purposes.

|proxy|status|
|---|---|
|_192.168.0.1:3000_||

## Maintaining this project

Now and then Twich changes it's elements ids, classes, etc. In order for the bot to work even after this changes, you need to change the value of a specific object in the _page_elements.json_ file.

Example:

```json
"username_input": {
  "type": "xPath",
  "value": "//div[contains(@data-a-target,'login-username-input')]/input"
},
```

_If you wan`t to help the project grow, you can create a PR request if some xPaths change in the future._

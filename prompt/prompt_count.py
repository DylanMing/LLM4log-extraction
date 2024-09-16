from vertexai.generative_models import (
    HarmCategory,
    HarmBlockThreshold,
)

# system_instruction = [
#     "you are a network specilist and informaticien.",
#     "your job is to extract all the text value of the following entities: {URL(domain)}, {IP}, {compuation resources} from a log file.",
#     "the contents must only include text strings found in the document.",
#     "each contents only appear in response one time. Please list them in different catagories.",
#     "the resulst should be in JSON format verified the response schema.",
#     "please distince the ip and urls, ips are all numbers and dots, and urls are strings,numbers and dots.",
#     "please find all the ip and url from the log file",
#     "don not make up IP and URL, they are real values from the log file.",
# ]

system_instruction = []

parameters = {
    "temperature": 0.2,
    "top_p": 0.8,
    # "top_k": 40
}

response_schema = {
    "type": "OBJECT",
    "properties": {
        "URL": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {"URL": {"type": "STRING"}, "count": {"type": "INTEGER"}},
            },
        },
        "IP": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {"IP": {"type": "STRING"}, "count": {"type": "INTEGER"}},
            },
        },
        "memory": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "Memory available": {"type": "STRING"},
                    "Memory total": {"type": "STRING"},
                    "apg memory": {"type": "STRING"},
                    "count": {"type": "INTEGER"},
                },
                "required": ["Memory available", "Memory total", "apg memory", "count"],
            },
        },
    },
    "required": ["URL", "IP", "memory"],
}

context = """You are a network specilist and informaticien. Your job is to extract all the text value of the following entities: {URL(domain)}, {IP}, {compuation resources} from a log file.
The resulst should be in JSON format verified the response schema.The IP and URL are extracted with their respective counts.
The contents must only include text strings found in the document.Each contents only appear in response one time. Please list them in different catagories.
Please distince the ip and urls, ips are all numbers and dots, and urls are strings,numbers and dots.",
Please find all the ip and url from the log file. Don not make up IP and URL, they are real values from the log file.
--------------------------------------------------
Here is some examples:
right example 1:
input text:
Aug  3 06:20:35 combo ftpd[28839]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005
Aug  3 06:20:35 combo ftpd[28839]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005
Aug  3 06:20:35 combo ftpd[28839]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005
output:
{
    "IP": [{"IP": "211.107.232.1", "count": "3"}],
    "URL": [],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning:
This is a right example because 211.107.232.1 is an IP address,appear 3 times, and there is no URL and memory mentioned in the input text.
---
right example 2:
input text:
Aug  4 07:00:29 combo sshd(pam_unix)[31674]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
Aug  4 07:00:29 combo sshd(pam_unix)[31675]: check pass; user unknown
Aug  4 07:00:29 combo sshd(pam_unix)[31675]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
Aug  4 07:00:29 combo sshd(pam_unix)[31676]: check pass; user unknown
output:
{
    "IP": [],
    "URL": [{"URL": "arx58.internetdsl.tpnet.pl","count":"2"}],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning:
This is a right example because arx58.internetdsl.tpnet.pl is an url,appear 2 times, and there is no IP and memory mentioned in the input text.
---
right example 3:
input text:
Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005
Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005
Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005
Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005
Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005
output:
{
    "IP": [{"IP":"82.53.83.190","count":"5"}],
    "URL": [{"URL":"host190-83.pool8253.interbusiness.it","count":"5"}],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning:
This is a right example because 82.53.83.190 is an IP address,appear 5 times, and host190-83.pool8253.interbusiness.it is an URL,appear 5 times. There is no memory mentioned in the input text.
---
right example 4:
input text:
Jun  9 06:06:20 combo kernel: Memory: 125312k/129720k available (1540k kernel code, 3860k reserved, 599k data, 144k init, 0k highmem)
Jun  9 06:06:21 combo kernel: agpgart: Maximum main memory to use for agp memory: 93M
output:
{
    "IP": [],
    "URL": []
    "memory": {"Memory available": "125312k", "Memory total": "129720k", "apg memory": "93M","count":"1"}
}
reasoning:
This is a right example because Memory: 125312k/129720k and agp memory: 93M are memory mentioned in the input text. There is no IP and URL mentioned in the input text.
---
wrong example 1:
input text:
Jan  9 17:35:55 combo ftpd[6505]: connection from 60.45.101.89 (p15025-ipadfx01yosida.nagano.ocn.ne.jp) at Mon Jan  9 17:35:55 2006
Jan  9 17:35:55 combo ftpd[6505]: connection from 60.45.101.89 (p15025-ipadfx01yosida.nagano.ocn.ne.jp) at Mon Jan  9 17:35:55 2006
Jan  9 17:35:55 combo ftpd[6505]: connection from 60.45.101.89 (p15025-ipadfx01yosida.nagano.ocn.ne.jp) at Mon Jan  9 17:35:55 2006
Jan  9 17:35:55 combo ftpd[6505]: connection from 60.45.101.89 (p15025-ipadfx01yosida.nagano.ocn.ne.jp) at Mon Jan  9 17:35:55 2006
output:
{
    "IP": [{"IP":"60.45.101.89","count":"4"},{"IP":"p15025-ipadfx01yosida.nagano.ocn.ne.jp","count":"4"}],
    "URL": []
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because 60.45.101.89 is an IP address,appear 4 times, p15025-ipadfx01yosida.nagano.ocn.ne.jp is an URL,appear 4 times. There is no memory mentioned in the input text.
---
wrong example 2:
input text:
Jul  9 22:53:19 combo ftpd[24085]: connection from 206.196.21.129 (host129.206.196.21.maximumasp.com) at Sat Jul  9 22:53:19 2005  
output:
{
    "IP": [],
    "URL": [{"URL":"206.196.21.129 (host129.206.196.21.maximumasp.com)","count":"1"}],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because 206.196.21.129 is a IP and host129.206.196.21.maximumasp.com is a URL,it should be seprate as an IP and an URL
---
wrong example 3:
input text:
Jul  9 22:53:22 combo ftpd[24073]: connection from 206.196.21.129 (host129.206.196.21.maximumasp.com) at Sat Jul  9 22:53:22 2005
Jul  9 22:53:22 combo ftpd[24073]: connection from 206.196.21.129 (host129.206.196.21.maximumasp.com) at Sat Jul  9 22:53:22 2005 
Jul 10 03:55:15 combo ftpd[24513]: connection from 217.187.83.139 () at Sun Jul 10 03:55:15 2005 
output:
{
    "IP": [{"IP":"206.196.21.129","count":"2"}],
    "URL": [{"URL":"host129.206.196.21.maximumasp.com","count":"2"}],
    "memory: {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because 217.187.83.139 is also an IP and appear 2 times
---
wrong example 4:
input text:
Oct  1 06:50:49 combo sshd(pam_unix)[12386]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=llekm-static-203.200.147.8.vsnl.net.in
Oct  1 06:50:49 combo sshd(pam_unix)[12386]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=llekm-static-203.200.147.8.vsnl.net.in
output:
{
    "IP": [{"IP":"203.200.147.8","count":"2"}],
    "URL": [{"URL":"llekm-static-203.200.147.8.vsnl.net.in","count":"2"}],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because 203.200.147.8 is a part of url llekm-static-203.200.147.8.vsnl.net.in, it should not be seperated as an IP
---
wrong example 5:
input text:
Nov 12 12:21:24 combo ftpd[32401]: connection from 64.27.5.9 (merton.whererwerunning.com) at Sat Nov 12 12:21:24 2005 
output:
{
    "IP": [{"IP":"64.27.5.9","count":"1"}],
    "URL": [{"URL":"merton.whererwerunning.com","count":"1"},[{"URL":"whererwerunning.com","count":"1"}],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because whererwerunning.com is a part of url merton.whererwerunning.com, it should not be seperated.
---
wrong example 6:
input text:
Feb  2 11:34:17 combo sshd(pam_unix)[3965]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=c-69-248-142-135.hsd1.nj.comcast.net
output:
{
    "IP": [{"IP":"c-69-248-142-135.hsd1.nj.comcast.net","count":"1"}],
    "URL": [],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because c-69-248-142-135.hsd1.nj.comcast.net is an url
-------
wrong example 7:
input text:
Aug  6 07:23:59 combo ftpd[10159]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
Aug  6 07:23:59 combo ftpd[10156]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
Aug  6 07:23:59 combo ftpd[10170]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
Aug  6 07:23:59 combo ftpd[10162]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
Aug  6 07:23:59 combo ftpd[10168]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
output:
{
    "IP": [{"IP":"211.107.232.1","count":"3"}],
    "URL": [],
    "memory": {"Memory available": "", "Memory total": "", "apg memory": "","count":""}
}
reasoning: this is a wrong example because 211.107.232.1 appear 5 times but extract 3 times


please extract all the IP, URL and memory from the input log file:

"""
safety_config = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

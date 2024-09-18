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
            "items": {"type": "STRING"},
        },
        "IP": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
        "memory": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "Memory available": {"type": "STRING"},
                    "Memory total": {"type": "STRING"},
                    "apg memory": {"type": "STRING"},
                },
                "required": ["Memory available", "Memory total", "apg memory"],
            },
        },
    },
    "required": ["URL", "IP", "memory"],
}

context = """You are a network specilist and informaticien. Your job is to extract all the text value of the following entities: {URL(domain)}, {IP}, {compuation resources} from a log file.
The contents must only include text strings found in the document.Each contents only appear in response one time. Please list them in different catagories.
The resulst should be in JSON format verified the response schema.Please distince the ip and urls, ips are all numbers and dots, and urls are strings,numbers and dots.",
Please find all the ip and url from the log file. Don not make up IP and URL, they are real values from the log file.
--------------------------------------------------
   "IP":["206-248-137-78.dsl.teksavvy.com"] is wrong!Don't consider "206-248-137-78.dsl.teksavvy.com" as IP.
    "URL":["206-248-137-78.dsl.teksavvy.com"] is correct.
    "URL":["202.101.42.106"] is wrong!Don't consider "202.101.42.106" as URL.
    "IP":["202.101.42.106"] is correct.
    -----------------------------------------------------------------------------------------------          
    example:
    Aug  3 04:03:17 combo su(pam_unix)[27339]: session closed for user cyrus
    Aug  3 04:03:18 combo logrotate: ALERT exited abnormally with [1]
    Aug  3 04:09:50 combo su(pam_unix)[28565]: session opened for user news by (uid=0)
    Aug  3 04:09:51 combo su(pam_unix)[28565]: session closed for user news
    Aug  3 06:20:34 combo ftpd[28835]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28827]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28823]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28834]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28832]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28824]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28825]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28821]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28831]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28826]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28828]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28829]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28822]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28833]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:34 combo ftpd[28830]: connection from 211.107.232.1 () at Wed Aug  3 06:20:34 2005 
    Aug  3 06:20:35 combo ftpd[28836]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005 
    Aug  3 06:20:35 combo ftpd[28839]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005 
    Aug  3 06:20:35 combo ftpd[28838]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005 
    Aug  3 06:20:35 combo ftpd[28837]: connection from 211.107.232.1 () at Wed Aug  3 06:20:35 2005 
    Aug  3 06:20:36 combo ftpd[28842]: connection from 211.107.232.1 () at Wed Aug  3 06:20:36 2005 
    Aug  3 06:20:36 combo ftpd[28841]: connection from 211.107.232.1 () at Wed Aug  3 06:20:36 2005 
    Aug  3 06:20:36 combo ftpd[28840]: connection from 211.107.232.1 () at Wed Aug  3 06:20:36 2005 
    Aug  4 04:03:35 combo su(pam_unix)[31009]: session opened for user cyrus by (uid=0)
    Aug  4 04:03:36 combo su(pam_unix)[31009]: session closed for user cyrus
    Aug  4 04:03:37 combo logrotate: ALERT exited abnormally with [1]
    Aug  4 04:09:30 combo su(pam_unix)[31380]: session opened for user news by (uid=0)
    Aug  4 04:09:31 combo su(pam_unix)[31380]: session closed for user news
    Aug  4 07:00:29 combo sshd(pam_unix)[31672]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31672]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31674]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31674]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31675]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31675]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31676]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31676]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31677]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31677]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31678]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31673]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31682]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31683]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31673]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31678]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31682]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31683]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 07:00:29 combo sshd(pam_unix)[31690]: check pass; user unknown
    Aug  4 07:00:29 combo sshd(pam_unix)[31690]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=arx58.internetdsl.tpnet.pl 
    Aug  4 11:01:11 combo sshd(pam_unix)[32057]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=202.96.242.5  user=root
    Aug  5 04:05:42 combo su(pam_unix)[1430]: session opened for user cyrus by (uid=0)
    Aug  5 04:05:42 combo su(pam_unix)[1430]: session closed for user cyrus
    Aug  5 04:05:43 combo logrotate: ALERT exited abnormally with [1]
    Aug  5 04:12:12 combo su(pam_unix)[2703]: session opened for user news by (uid=0)
    Aug  5 04:12:13 combo su(pam_unix)[2703]: session closed for user news
    Aug  5 05:01:30 combo login(pam_unix)[25160]: bad username [   ]
    Aug  5 05:01:30 combo login[25160]: FAILED LOGIN 1 FROM (null) FOR    , Authentication failure
    Aug  5 05:01:30 combo login(pam_unix)[25160]: bad username []
    Aug  5 05:01:30 combo login[25160]: FAILED LOGIN 2 FROM (null) FOR , Authentication failure
    Aug  5 05:02:30 combo udev[2877]: removing device node '/udev/vcs2'
    Aug  5 05:02:30 combo udev[2878]: removing device node '/udev/vcsa2'
    Aug  5 05:02:30 combo udev[2887]: creating device node '/udev/vcs2'
    Aug  5 05:02:30 combo udev[2888]: creating device node '/udev/vcsa2'
    Aug  5 05:02:30 combo udev[2895]: removing device node '/udev/vcs2'
    Aug  5 05:02:30 combo udev[2903]: removing device node '/udev/vcsa2'
    Aug  5 05:02:31 combo udev[2900]: creating device node '/udev/vcs2'
    Aug  5 05:02:31 combo udev[2908]: creating device node '/udev/vcsa2'
    Aug  5 12:03:56 combo sshd(pam_unix)[3501]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=202.96.242.5  user=root
    Aug  5 12:04:13 combo sshd(pam_unix)[3504]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=202.96.242.5  user=root
    Aug  6 04:03:29 combo su(pam_unix)[5193]: session opened for user cyrus by (uid=0)
    Aug  6 04:03:30 combo su(pam_unix)[5193]: session closed for user cyrus
    Aug  6 04:03:30 combo logrotate: ALERT exited abnormally with [1]
    Aug  6 04:11:21 combo su(pam_unix)[9843]: session opened for user news by (uid=0)
    Aug  6 04:11:22 combo su(pam_unix)[9843]: session closed for user news
    Aug  6 07:23:59 combo ftpd[10159]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10156]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10170]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10162]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10168]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10166]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10155]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10167]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10160]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10165]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10164]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10161]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10169]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10153]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10163]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10157]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10158]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10154]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  6 07:23:59 combo ftpd[10152]: connection from 211.107.232.1 () at Sat Aug  6 07:23:59 2005 
    Aug  7 04:03:36 combo su(pam_unix)[12320]: session opened for user cyrus by (uid=0)
    Aug  7 04:03:37 combo su(pam_unix)[12320]: session closed for user cyrus
    Aug  7 04:03:39 combo cups: cupsd shutdown succeeded
    Aug  7 04:03:45 combo cups: cupsd startup succeeded
    Aug  7 04:03:57 combo syslogd 1.4.1: restart.
    Aug  7 04:03:57 combo logrotate: ALERT exited abnormally with [1]
    Aug  7 04:09:31 combo su(pam_unix)[12914]: session opened for user news by (uid=0)
    Aug  7 04:09:32 combo su(pam_unix)[12914]: session closed for user news
    Aug  7 06:52:07 combo ftpd[16258]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16249]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16254]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16259]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16257]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16256]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16260]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16255]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16248]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16244]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16243]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16247]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16242]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16252]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16241]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16250]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005 
    Aug  7 06:52:07 combo ftpd[16253]: connection from 82.53.83.190 (host190-83.pool8253.interbusiness.it) at Sun Aug  7 06:52:07 2005            

    output:
    {"URL":["arx58.internetdsl.tpnet.pl", "host190-83.pool8253.interbusiness.it"],
    "IP":["211.107.232.1", "202.96.242.5", "82.53.83.190"],
    "memory":["125312k/129720k available",],
    }
-------
please extract all the IP, URL and memory from the input log file:

"""
safety_config = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


import asyncio
import sys
from typing import Union, Dict, List

import requests
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from rich.console import Console
from rich.pretty import pprint

from database import AsyncMongo


class SubjectMarks:
    def __init__(
            self,
            subject: Dict[str, Union[str, int]]
    ):
        self.subject_name = subject.get("subject_name")
        self.subject_abbr = subject.get("subject_abbr")
        self.mark = subject.get("mark")


class Result:
    def __init__(self, data: Dict[str, Union[str, List[Dict[str, str]]]]) -> None:
        self.gender = data.get("gender")
        self.id = data.get('id')
        self.name = data.get('name')
        self.registration_number = data.get("registration_number")
        self.stream = data.get("stream")
        self.school = data.get("school")
        self.total = data.get("total")
        self.subject_marks = data['subject_marks']

    def get_subjects(self) -> List[SubjectMarks]:
        return [SubjectMarks(subject) for subject in self.subject_marks]


class RegistrationNumberNotFound(Exception):
    pass


class Neaea:
    def __init__(self, mongo: Union[AsyncMongo, str], proxy: Dict[str, str] = None) -> None:
        self._s = requests.session()
        self._console = Console()
        self._log = self._console.log
        self._neaea_url = "https://result.ethernet.edu.et/index.php"
        self._ua = UserAgent()
        self._mogo_uri = mongo
        self._mongo = AsyncMongo(self._mogo_uri, "NEAEA") if isinstance(mongo, str) else mongo
        self._proxies = proxy
        self._headers = {
            "Host": "result.ethernet.edu.et",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "",
            "Content-Length": "",
            "User-Agent": "",
            "Origin": "https://result.ethernet.edu.et",
            "Referer": "https://result.ethernet.edu.et/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _get_post_data(self, reg_no: Union[str, int]) -> MultipartEncoder:
        return MultipartEncoder(
            fields={
                "registration_number": str(reg_no),
            }
        )

    async def _save_result(self, reg_no: Union[str, int], data: Dict[str, Union[str, List[Dict[str, str]]]]) -> None:
        self._log("Saving to DB Reg No: {}".format(reg_no))
        await self._mongo.insert(
            "RESULTS",
            {
                "REG_NO": str(reg_no),
                "DATA": data
            }
        )

    async def get_result(self, reg_no: Union[str, int]) -> Result:
        if result := await self._mongo.find_one(
                "RESULTS",
                {
                    "REG_NO": str(reg_no)
                }
        ):
            self._log("Found in DB Reg No: {}".format(reg_no))
            return Result(result['DATA'])

        _multipart_data = self._get_post_data(reg_no)
        self._headers["Content-Type"] = _multipart_data.content_type
        self._headers["Content-Length"] = str(_multipart_data.len)
        self._headers["User-Agent"] = self._ua.random
        res = self._s.post(
            self._neaea_url,
            data=_multipart_data.to_string(),
            headers=self._headers,
            proxies=self._proxies,
        )
        if res.status_code == 200:
            await self._save_result(reg_no, res.json())
            return Result(res.json())
        raise RegistrationNumberNotFound(f"{res.status_code} {res.text}")


async def main() -> None:
    neaea = Neaea(
        mongo="mongodb://localhost:27017/",
    )
    result = await neaea.get_result("424450")
    pprint(result.name)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(main())
    asyncio.get_event_loop().close()
    sys.exit(0)

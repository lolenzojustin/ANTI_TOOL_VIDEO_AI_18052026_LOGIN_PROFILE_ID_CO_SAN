import requests
import time
import shutil
import os
import subprocess
import threading

PORT_LOCK = threading.Lock()
NEXT_PORT = 40444

def get_next_port():
    global NEXT_PORT
    with PORT_LOCK:
        port = NEXT_PORT
        NEXT_PORT += 1
        return port
    

# API_URL = "http://localhost:9495"  # URL mặc định của GPM Global API trên máy local
class Gpm:
    def __init__(self) -> None:
        pass
    def get_new_payload(self,proxy, win_size="1280,800"):
        res = win_size.replace(",", "x")
        payload = {
            "name": "Test profile from api",
            "group_id": None,
            "raw_proxy": proxy,               # IP:Port:User:Pass hoặc tm://API_KEY|True,False ...
            "browser_type": 1,                # 1: Chromium, 2: Firefox
            "browser_version": "147.0.7727.56",
            "os_type": 1,                     # 1: Windows, 2: MacOS, 3: Linux
            "screen_resolution": res,
            "custom_user_agent": None,
            "task_bar_title": "abc",
            "webrtc_mode": None,
            "fixed_webrtc_public_ip": "",
            "geolocation_mode": None,
            "canvas_mode": None,
            "client_rect_mode": None,
            "webgl_image_mode": None,
            "webgl_metadata_mode": None,
            "audio_mode": None,
            "font_mode": None,
            "timezone_base_on_ip": True,
            "timezone": None,
            "is_language_base_on_ip": True,
            "fixed_language": None
        }
        return payload
    def get_new_payload_2(self, win_size="1280,800"):
        res = win_size.replace(",", "x")
        payload = {
            "name": "Test profile from api",
            "group_id": None,
            "raw_proxy": "",               # IP:Port:User:Pass hoặc tm://API_KEY|True,False ...
            "browser_type": 1,                # 1: Chromium, 2: Firefox
            "browser_version": "147.0.7727.56",
            "os_type": 1,                     # 1: Windows, 2: MacOS, 3: Linux
            "screen_resolution": res,
            "custom_user_agent": None,
            "task_bar_title": "abc",
            "webrtc_mode": None,
            "fixed_webrtc_public_ip": "",
            "geolocation_mode": None,
            "canvas_mode": None,
            "client_rect_mode": None,
            "webgl_image_mode": None,
            "webgl_metadata_mode": None,
            "audio_mode": None,
            "font_mode": None,
            "timezone_base_on_ip": True,
            "timezone": None,
            "is_language_base_on_ip": True,
            "fixed_language": None
        }
        return payload
    def get_profiles(self, apiurl_Gpm, page=1, per_page=30, search="", sort=0):
        params_get_profiles = {
            "page": page,
            "per_page": per_page,
            "search": search,
            "sort": sort
        }

        response = requests.get(
            apiurl_Gpm + "/api/v1/profiles",
            params=params_get_profiles,
            timeout=30
        ).json()

        print("danh sách profiles:", response)
        return response


    def get_profile(self, apiurl_Gpm, id_profile):
        response = requests.get(
            f"{apiurl_Gpm}/api/v1/profiles/{id_profile}",
            timeout=30
        ).json()

        print("thông tin profile:", response)
        return response
    def create_profile(self,apiurl_Gpm,proxy, win_size="1280,800"):
        new_payload = self.get_new_payload(proxy, win_size)
        headers = {
        "Content-Type": "application/json"
    }
        response = requests.post(
            apiurl_Gpm + "/api/v1/profiles/create",
            json=new_payload,
            headers=headers,
            timeout=30
        ).json()
        id_profile = response["data"]["id"]
        print("tạo id_profile là",id_profile)
        return id_profile
    
    def create_profile_2(self,apiurl_Gpm, win_size="1280,800"):
        new_payload = self.get_new_payload_2(win_size)
        headers = {
        "Content-Type": "application/json"
    }
        response = requests.post(
            apiurl_Gpm + "/api/v1/profiles/create",
            json=new_payload,
            headers=headers,
            timeout=30
        ).json()
        id_profile = response["data"]["id"]
        print("tạo id_profile là",id_profile)
        return id_profile  
    # def open_profile(self,apiurl_Gpm, id_profile, win_pos, win_size):
    #     extension_dir = r"C:\Users\PC\Desktop\nopecha"
    #     add_args = f'--load-extension="{extension_dir}"'
    #     params_open_profile = {
    #         "addination_args": add_args,
    #         "win_scale": 1.0,
    #         "win_pos": win_pos,
    #         "win_size": win_size,
    #     }

    #     url = f"{apiurl_Gpm}/api/v1/profiles/start/{id_profile}"

    #     response = requests.get(url, params=params_open_profile).json()
    #     remote_debugging_address = response["data"]["remote_debugging_address"]
    #     return remote_debugging_address


    def open_profile(self, apiurl_Gpm, id_profile, win_pos="0,0", win_size="1280,800", link_nopecha=""):
        # extension_dir = r"C:\Users\Admin\OneDrive\Desktop\nopecha"
        extension_dir = link_nopecha

        # Chỉ thêm --load-extension nếu có đường dẫn extension
        if extension_dir:
            add_args = (
                f'--load-extension="{extension_dir}" '
                f'--window-position={win_pos} '
                f'--window-size={win_size}'
            )
        else:
            add_args = (
                f'--window-position={win_pos} '
                f'--window-size={win_size}'
            )

        remote_port = get_next_port()

        params_open_profile = {
            "remote_debugging_port": remote_port,
            "window_scale": 0.99,
            "window_pos": win_pos,
            "window_size": win_size,
            "addition_args": add_args,
        }

        url = f"{apiurl_Gpm}/api/v1/profiles/start/{id_profile}"

        response = requests.get(
            url,
            params=params_open_profile,
            timeout=30
        ).json()

        print("win_pos:", win_pos)
        print("win_size:", win_size)
        print("response open_profile:", response)

        data = response.get("data", {})
        remote_debugging_port = data.get("remote_debugging_port")

        if not remote_debugging_port:
            print("Không có remote_debugging_port trong data")
            return None

        remote_debugging_address = f"127.0.0.1:{remote_debugging_port}"
        return remote_debugging_address





    def close_profile(self, apiurl_Gpm, id_profile):
        response = requests.get(
            f"{apiurl_Gpm}/api/v1/profiles/stop/{id_profile}",
            timeout=30
        ).json()
        print("đóng profile:", response)
        return response
    def update_profile(self, apiurl_Gpm, id_profile, proxy=""):
        payload = self.get_new_payload(proxy)

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{apiurl_Gpm}/api/v1/profiles/update/{id_profile}",
            json=payload,
            headers=headers,
            timeout=30
        ).json()

        print("update profile:", response)
        return response
    def delete_profile(self, apiurl_Gpm, id_profile, mode="hard"):
        response = requests.get(
            f"{apiurl_Gpm}/api/v1/profiles/delete/{id_profile}",
            params={"mode": mode},
            timeout=30
        ).json()

        print("xóa id_profile là", id_profile)
        print("response delete:", response)
        return response



# if __name__ == "__main__":
#     g = Gpm()
#     apiurl_Gpm = API_URL
#     proxy = ""  # Nếu không dùng proxy thì để rỗng
#     # proxy = "ip:port:user:pass"  # Nếu dùng proxy thì điền vào đây
#     # Bước 1: Tạo profile
#     id_profile = g.create_profile(apiurl_Gpm, proxy)
#     print("đã tạo profile")
#     time.sleep(2)
#     # Bước 2: Mở profile
#     remote_debugging_address = g.open_profile(
#         apiurl_Gpm=apiurl_Gpm,
#         id_profile=id_profile,
#         win_pos="0,0",
#         win_size="800,600"
#     )
#     print("đã mở profile vừa tạo")
#     print("remote_debugging_address:", remote_debugging_address)
#     time.sleep(2)
#     # Bước 3: Đóng profile
#     g.close_profile(apiurl_Gpm, id_profile)
#     print("đã đóng profile vừa tạo")
#     time.sleep(2)
#     # Bước 4: Update profile
#     g.update_profile(apiurl_Gpm, id_profile)
#     print("đã update profile vừa tạo")
#     time.sleep(2)
#     # Bước 5: Xóa profile
#     g.delete_profile(apiurl_Gpm, id_profile)
#     print("đã xóa profile vừa tạo")
#     time.sleep(1000)

# test9
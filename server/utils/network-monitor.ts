/**
 * Network monitoring utilities for AetherLink
 * Provides real network data collection from local network
 */

import arp from "node-arp";
import si from "systeminformation";
import { exec } from "child_process";
import { promisify } from "util";
import dns from "dns";

const execAsync = promisify(exec);
const dnsReverse = promisify(dns.reverse);

// MAC OUI database for vendor identification
const macVendors: Record<string, { vendor: string; type?: string }> = {
  "00:03:93": { vendor: "Apple", type: "phone" },
  "00:05:02": { vendor: "Apple", type: "phone" },
  "00:0a:95": { vendor: "Apple", type: "laptop" },
  "00:0d:93": { vendor: "Apple", type: "laptop" },
  "00:11:24": { vendor: "Apple", type: "laptop" },
  "00:14:51": { vendor: "Apple", type: "laptop" },
  "00:16:cb": { vendor: "Apple", type: "laptop" },
  "00:17:f2": { vendor: "Apple", type: "laptop" },
  "00:19:e3": { vendor: "Apple", type: "laptop" },
  "00:1b:63": { vendor: "Apple", type: "laptop" },
  "00:1c:b3": { vendor: "Apple", type: "laptop" },
  "00:1d:4f": { vendor: "Apple", type: "laptop" },
  "00:1e:52": { vendor: "Apple", type: "laptop" },
  "00:1f:5b": { vendor: "Apple", type: "laptop" },
  "00:1f:f3": { vendor: "Apple", type: "laptop" },
  "00:21:e9": { vendor: "Apple", type: "laptop" },
  "00:22:41": { vendor: "Apple", type: "laptop" },
  "00:23:12": { vendor: "Apple", type: "laptop" },
  "00:23:32": { vendor: "Apple", type: "laptop" },
  "00:23:6c": { vendor: "Apple", type: "laptop" },
  "00:23:df": { vendor: "Apple", type: "laptop" },
  "00:24:36": { vendor: "Apple", type: "laptop" },
  "00:25:00": { vendor: "Apple", type: "laptop" },
  "00:25:4b": { vendor: "Apple", type: "laptop" },
  "00:25:bc": { vendor: "Apple", type: "laptop" },
  "00:26:08": { vendor: "Apple", type: "laptop" },
  "00:26:4a": { vendor: "Apple", type: "laptop" },
  "00:26:b0": { vendor: "Apple", type: "laptop" },
  "00:26:bb": { vendor: "Apple", type: "laptop" },
  "00:3e:e1": { vendor: "Apple", type: "phone" },
  "00:50:e4": { vendor: "Apple", type: "laptop" },
  "00:61:71": { vendor: "Apple", type: "phone" },
  "00:88:65": { vendor: "Apple", type: "phone" },
  "00:a0:40": { vendor: "Apple", type: "laptop" },
  "00:cd:fe": { vendor: "Apple", type: "phone" },
  "00:f4:b9": { vendor: "Apple", type: "phone" },
  "04:0c:ce": { vendor: "Apple", type: "phone" },
  "04:15:52": { vendor: "Apple", type: "laptop" },
  "04:26:65": { vendor: "Apple", type: "laptop" },
  "04:d3:cf": { vendor: "Apple", type: "phone" },
  "04:db:56": { vendor: "Apple", type: "phone" },
  "04:e5:36": { vendor: "Apple", type: "phone" },
  "08:00:07": { vendor: "Apple", type: "laptop" },
  "08:66:98": { vendor: "Apple", type: "phone" },
  "08:70:45": { vendor: "Apple", type: "phone" },
  "0c:3e:9f": { vendor: "Apple", type: "phone" },
  "0c:4d:e9": { vendor: "Apple", type: "phone" },
  "0c:74:c2": { vendor: "Apple", type: "phone" },
  "10:40:f3": { vendor: "Apple", type: "phone" },
  "10:93:e9": { vendor: "Apple", type: "phone" },
  "10:9a:dd": { vendor: "Apple", type: "phone" },
  "10:dd:b1": { vendor: "Apple", type: "phone" },
  "14:10:9f": { vendor: "Apple", type: "phone" },
  "14:8f:c6": { vendor: "Apple", type: "phone" },
  "14:bd:61": { vendor: "Apple", type: "phone" },
  "18:20:32": { vendor: "Apple", type: "phone" },
  "18:34:51": { vendor: "Apple", type: "phone" },
  "18:e7:f4": { vendor: "Apple", type: "phone" },
  "1c:36:bb": { vendor: "Apple", type: "phone" },
  "1c:ab:a7": { vendor: "Apple", type: "phone" },
  "20:3c:ae": { vendor: "Apple", type: "phone" },
  "20:76:93": { vendor: "Apple", type: "phone" },
  "20:ab:37": { vendor: "Apple", type: "phone" },
  "20:c9:d0": { vendor: "Apple", type: "phone" },
  "24:a0:74": { vendor: "Apple", type: "phone" },
  "24:a2:e1": { vendor: "Apple", type: "phone" },
  "24:ab:81": { vendor: "Apple", type: "phone" },
  "28:37:37": { vendor: "Apple", type: "phone" },
  "28:6a:b8": { vendor: "Apple", type: "phone" },
  "28:a0:2b": { vendor: "Apple", type: "phone" },
  "28:cf:e9": { vendor: "Apple", type: "phone" },
  "28:e1:4c": { vendor: "Apple", type: "phone" },
  "28:ed:6a": { vendor: "Apple", type: "phone" },
  "28:f0:76": { vendor: "Apple", type: "phone" },
  "2c:1f:23": { vendor: "Apple", type: "phone" },
  "2c:33:61": { vendor: "Apple", type: "phone" },
  "2c:be:08": { vendor: "Apple", type: "phone" },
  "2c:f0:a2": { vendor: "Apple", type: "phone" },
  "30:10:e4": { vendor: "Apple", type: "phone" },
  "30:35:ad": { vendor: "Apple", type: "phone" },
  "30:90:ab": { vendor: "Apple", type: "phone" },
  "34:15:9e": { vendor: "Apple", type: "phone" },
  "34:36:3b": { vendor: "Apple", type: "phone" },
  "34:a3:95": { vendor: "Apple", type: "phone" },
  "38:48:4c": { vendor: "Apple", type: "phone" },
  "38:c9:86": { vendor: "Apple", type: "phone" },
  "3c:07:54": { vendor: "Apple", type: "phone" },
  "3c:15:c2": { vendor: "Apple", type: "phone" },
  "3c:2e:f9": { vendor: "Apple", type: "phone" },
  "40:30:04": { vendor: "Apple", type: "phone" },
  "40:33:1a": { vendor: "Apple", type: "phone" },
  "40:4d:7f": { vendor: "Apple", type: "phone" },
  "40:83:1d": { vendor: "Apple", type: "phone" },
  "40:a6:d9": { vendor: "Apple", type: "phone" },
  "40:b3:95": { vendor: "Apple", type: "phone" },
  "44:00:10": { vendor: "Apple", type: "phone" },
  "44:2a:60": { vendor: "Apple", type: "phone" },
  "44:4c:0c": { vendor: "Apple", type: "phone" },
  "48:43:7c": { vendor: "Apple", type: "phone" },
  "48:60:bc": { vendor: "Apple", type: "phone" },
  "48:74:6e": { vendor: "Apple", type: "phone" },
  "48:a1:95": { vendor: "Apple", type: "phone" },
  "4c:57:ca": { vendor: "Apple", type: "phone" },
  "4c:74:bf": { vendor: "Apple", type: "phone" },
  "4c:8d:79": { vendor: "Apple", type: "phone" },
  "50:32:37": { vendor: "Apple", type: "phone" },
  "50:ea:d6": { vendor: "Apple", type: "phone" },
  "54:26:96": { vendor: "Apple", type: "phone" },
  "54:4e:90": { vendor: "Apple", type: "phone" },
  "54:72:4f": { vendor: "Apple", type: "phone" },
  "54:ae:27": { vendor: "Apple", type: "phone" },
  "54:ea:a8": { vendor: "Apple", type: "phone" },
  "58:1f:aa": { vendor: "Apple", type: "phone" },
  "58:40:4e": { vendor: "Apple", type: "phone" },
  "58:55:ca": { vendor: "Apple", type: "phone" },
  "58:b0:35": { vendor: "Apple", type: "phone" },
  "5c:59:48": { vendor: "Apple", type: "phone" },
  "5c:95:ae": { vendor: "Apple", type: "phone" },
  "5c:96:9d": { vendor: "Apple", type: "phone" },
  "5c:f9:38": { vendor: "Apple", type: "phone" },
  "60:03:08": { vendor: "Apple", type: "phone" },
  "60:33:4b": { vendor: "Apple", type: "phone" },
  "60:69:44": { vendor: "Apple", type: "phone" },
  "60:92:17": { vendor: "Apple", type: "phone" },
  "60:c5:47": { vendor: "Apple", type: "phone" },
  "60:f8:1d": { vendor: "Apple", type: "phone" },
  "60:fa:cd": { vendor: "Apple", type: "phone" },
  "60:fb:42": { vendor: "Apple", type: "phone" },
  "64:20:0c": { vendor: "Apple", type: "phone" },
  "64:76:ba": { vendor: "Apple", type: "phone" },
  "64:a3:cb": { vendor: "Apple", type: "phone" },
  "64:b9:e8": { vendor: "Apple", type: "phone" },
  "64:e6:82": { vendor: "Apple", type: "phone" },
  "68:09:27": { vendor: "Apple", type: "phone" },
  "68:5b:35": { vendor: "Apple", type: "phone" },
  "68:96:7b": { vendor: "Apple", type: "phone" },
  "68:a8:6d": { vendor: "Apple", type: "phone" },
  "68:d9:3c": { vendor: "Apple", type: "phone" },
  "6c:19:c0": { vendor: "Apple", type: "phone" },
  "6c:3e:6d": { vendor: "Apple", type: "phone" },
  "6c:40:08": { vendor: "Apple", type: "phone" },
  "6c:4d:73": { vendor: "Apple", type: "phone" },
  "6c:70:9f": { vendor: "Apple", type: "phone" },
  "6c:72:e7": { vendor: "Apple", type: "phone" },
  "6c:94:66": { vendor: "Apple", type: "phone" },
  "6c:96:cf": { vendor: "Apple", type: "phone" },
  "70:11:24": { vendor: "Apple", type: "phone" },
  "70:3e:ac": { vendor: "Apple", type: "phone" },
  "70:48:0f": { vendor: "Apple", type: "phone" },
  "70:73:cb": { vendor: "Apple", type: "phone" },
  "70:de:e2": { vendor: "Apple", type: "phone" },
  "70:ec:e4": { vendor: "Apple", type: "phone" },
  "74:1b:b2": { vendor: "Apple", type: "phone" },
  "74:e1:b6": { vendor: "Apple", type: "phone" },
  "74:e2:f5": { vendor: "Apple", type: "phone" },
  "78:31:c1": { vendor: "Apple", type: "phone" },
  "78:7b:8a": { vendor: "Apple", type: "phone" },
  "78:a3:e4": { vendor: "Apple", type: "phone" },
  "78:ca:39": { vendor: "Apple", type: "phone" },
  "78:d7:5f": { vendor: "Apple", type: "phone" },
  "78:fd:94": { vendor: "Apple", type: "phone" },
  "7c:01:91": { vendor: "Apple", type: "phone" },
  "7c:04:d0": { vendor: "Apple", type: "phone" },
  "7c:11:be": { vendor: "Apple", type: "phone" },
  "7c:6d:f8": { vendor: "Apple", type: "phone" },
  "7c:c3:a1": { vendor: "Apple", type: "phone" },
  "7c:c5:37": { vendor: "Apple", type: "phone" },
  "7c:d1:c3": { vendor: "Apple", type: "phone" },
  "7c:f0:5f": { vendor: "Apple", type: "phone" },
  "80:49:71": { vendor: "Apple", type: "phone" },
  "80:92:9f": { vendor: "Apple", type: "phone" },
  "80:be:05": { vendor: "Apple", type: "phone" },
  "80:d6:05": { vendor: "Apple", type: "phone" },
  "80:e6:50": { vendor: "Apple", type: "phone" },
  "84:29:99": { vendor: "Apple", type: "phone" },
  "84:38:35": { vendor: "Apple", type: "phone" },
  "84:78:8b": { vendor: "Apple", type: "phone" },
  "84:85:06": { vendor: "Apple", type: "phone" },
  "84:8e:0c": { vendor: "Apple", type: "phone" },
  "84:fc:fe": { vendor: "Apple", type: "phone" },
  "88:1f:a1": { vendor: "Apple", type: "phone" },
  "88:53:95": { vendor: "Apple", type: "phone" },
  "88:66:5a": { vendor: "Apple", type: "phone" },
  "88:63:df": { vendor: "Apple", type: "phone" },
  "88:cb:87": { vendor: "Apple", type: "phone" },
  "88:e8:7f": { vendor: "Apple", type: "phone" },
  "8c:00:6d": { vendor: "Apple", type: "phone" },
  "8c:29:37": { vendor: "Apple", type: "phone" },
  "8c:7c:92": { vendor: "Apple", type: "phone" },
  "8c:85:90": { vendor: "Apple", type: "phone" },
  "8c:8e:f2": { vendor: "Apple", type: "phone" },
  "90:27:e4": { vendor: "Apple", type: "phone" },
  "90:72:40": { vendor: "Apple", type: "phone" },
  "90:8d:6c": { vendor: "Apple", type: "phone" },
  "90:b0:ed": { vendor: "Apple", type: "phone" },
  "90:b2:1f": { vendor: "Apple", type: "phone" },
  "94:e9:6a": { vendor: "Apple", type: "phone" },
  "98:01:a7": { vendor: "Apple", type: "phone" },
  "98:03:d8": { vendor: "Apple", type: "phone" },
  "98:5a:eb": { vendor: "Apple", type: "phone" },
  "98:b8:e3": { vendor: "Apple", type: "phone" },
  "98:f0:ab": { vendor: "Apple", type: "phone" },
  "9c:04:eb": { vendor: "Apple", type: "phone" },
  "9c:20:7b": { vendor: "Apple", type: "phone" },
  "9c:35:5b": { vendor: "Apple", type: "phone" },
  "9c:84:bf": { vendor: "Apple", type: "phone" },
  "9c:f4:8e": { vendor: "Apple", type: "phone" },
  "a0:2d:c4": { vendor: "Apple", type: "phone" },
  "a0:4e:a7": { vendor: "Apple", type: "phone" },
  "a0:99:9b": { vendor: "Apple", type: "phone" },
  "a0:d7:95": { vendor: "Apple", type: "phone" },
  "a4:31:35": { vendor: "Apple", type: "phone" },
  "a4:5e:60": { vendor: "Apple", type: "phone" },
  "a4:67:06": { vendor: "Apple", type: "phone" },
  "a4:b1:97": { vendor: "Apple", type: "phone" },
  "a4:c3:61": { vendor: "Apple", type: "phone" },
  "a4:d1:8c": { vendor: "Apple", type: "phone" },
  "a8:20:66": { vendor: "Apple", type: "phone" },
  "a8:5b:78": { vendor: "Apple", type: "phone" },
  "a8:5c:2c": { vendor: "Apple", type: "phone" },
  "a8:66:7f": { vendor: "Apple", type: "phone" },
  "a8:88:08": { vendor: "Apple", type: "phone" },
  "a8:96:8a": { vendor: "Apple", type: "phone" },
  "a8:be:27": { vendor: "Apple", type: "phone" },
  "a8:fa:d8": { vendor: "Apple", type: "phone" },
  "ac:1f:74": { vendor: "Apple", type: "phone" },
  "ac:29:3a": { vendor: "Apple", type: "phone" },
  "ac:3c:0b": { vendor: "Apple", type: "phone" },
  "ac:61:ea": { vendor: "Apple", type: "phone" },
  "ac:87:a3": { vendor: "Apple", type: "phone" },
  "ac:bc:32": { vendor: "Apple", type: "phone" },
  "ac:cf:5c": { vendor: "Apple", type: "phone" },
  "b0:34:95": { vendor: "Apple", type: "phone" },
  "b0:65:bd": { vendor: "Apple", type: "phone" },
  "b0:9f:ba": { vendor: "Apple", type: "phone" },
  "b4:18:d1": { vendor: "Apple", type: "phone" },
  "b4:8b:19": { vendor: "Apple", type: "phone" },
  "b4:f0:ab": { vendor: "Apple", type: "phone" },
  "b4:f6:1c": { vendor: "Apple", type: "phone" },
  "b8:09:8a": { vendor: "Apple", type: "phone" },
  "b8:17:c2": { vendor: "Apple", type: "phone" },
  "b8:41:a4": { vendor: "Apple", type: "phone" },
  "b8:53:ac": { vendor: "Apple", type: "phone" },
  "b8:5d:0a": { vendor: "Apple", type: "phone" },
  "b8:63:4d": { vendor: "Apple", type: "phone" },
  "b8:78:2e": { vendor: "Apple", type: "phone" },
  "b8:c1:11": { vendor: "Apple", type: "phone" },
  "b8:e8:56": { vendor: "Apple", type: "phone" },
  "b8:f6:b1": { vendor: "Apple", type: "phone" },
  "bc:3b:af": { vendor: "Apple", type: "phone" },
  "bc:52:b7": { vendor: "Apple", type: "phone" },
  "bc:67:78": { vendor: "Apple", type: "phone" },
  "bc:6c:21": { vendor: "Apple", type: "phone" },
  "bc:92:6b": { vendor: "Apple", type: "phone" },
  "bc:9f:ef": { vendor: "Apple", type: "phone" },
  "bc:ec:5d": { vendor: "Apple", type: "phone" },
  "c0:1a:da": { vendor: "Apple", type: "phone" },
  "c0:63:94": { vendor: "Apple", type: "phone" },
  "c0:84:7d": { vendor: "Apple", type: "phone" },
  "c0:9f:42": { vendor: "Apple", type: "phone" },
  "c0:b6:58": { vendor: "Apple", type: "phone" },
  "c0:cc:f8": { vendor: "Apple", type: "phone" },
  "c0:d0:12": { vendor: "Apple", type: "phone" },
  "c0:f2:fb": { vendor: "Apple", type: "phone" },
  "c4:2c:03": { vendor: "Apple", type: "phone" },
  "c4:61:8b": { vendor: "Apple", type: "phone" },
  "c8:2a:14": { vendor: "Apple", type: "phone" },
  "c8:33:4b": { vendor: "Apple", type: "phone" },
  "c8:69:cd": { vendor: "Apple", type: "phone" },
  "c8:85:50": { vendor: "Apple", type: "phone" },
  "c8:b5:b7": { vendor: "Apple", type: "phone" },
  "c8:bc:c8": { vendor: "Apple", type: "phone" },
  "cc:08:8d": { vendor: "Apple", type: "phone" },
  "cc:20:e8": { vendor: "Apple", type: "phone" },
  "cc:25:ef": { vendor: "Apple", type: "phone" },
  "cc:29:f5": { vendor: "Apple", type: "phone" },
  "cc:2d:b7": { vendor: "Apple", type: "phone" },
  "cc:78:5f": { vendor: "Apple", type: "phone" },
  "d0:03:4b": { vendor: "Apple", type: "phone" },
  "d0:23:db": { vendor: "Apple", type: "phone" },
  "d0:25:98": { vendor: "Apple", type: "phone" },
  "d0:33:11": { vendor: "Apple", type: "phone" },
  "d0:4f:7e": { vendor: "Apple", type: "phone" },
  "d0:81:7a": { vendor: "Apple", type: "phone" },
  "d0:a6:37": { vendor: "Apple", type: "phone" },
  "d0:c5:f3": { vendor: "Apple", type: "phone" },
  "d4:9a:20": { vendor: "Apple", type: "phone" },
  "d4:a3:3d": { vendor: "Apple", type: "phone" },
  "d4:dc:cd": { vendor: "Apple", type: "phone" },
  "d4:f4:6f": { vendor: "Apple", type: "phone" },
  "d8:1c:79": { vendor: "Apple", type: "phone" },
  "d8:30:62": { vendor: "Apple", type: "phone" },
  "d8:9e:3f": { vendor: "Apple", type: "phone" },
  "d8:a2:5e": { vendor: "Apple", type: "phone" },
  "d8:bb:2c": { vendor: "Apple", type: "phone" },
  "dc:09:4c": { vendor: "Apple", type: "phone" },
  "dc:0c:5c": { vendor: "Apple", type: "phone" },
  "dc:2b:2a": { vendor: "Apple", type: "phone" },
  "dc:2b:61": { vendor: "Apple", type: "phone" },
  "dc:37:18": { vendor: "Apple", type: "phone" },
  "dc:3d:24": { vendor: "Apple", type: "phone" },
  "dc:56:e7": { vendor: "Apple", type: "phone" },
  "dc:86:d8": { vendor: "Apple", type: "phone" },
  "dc:a4:ca": { vendor: "Apple", type: "phone" },
  "dc:a9:04": { vendor: "Apple", type: "phone" },
  "dc:bf:e0": { vendor: "Apple", type: "phone" },
  "e0:5f:45": { vendor: "Apple", type: "phone" },
  "e0:66:78": { vendor: "Apple", type: "phone" },
  "e0:99:71": { vendor: "Apple", type: "phone" },
  "e0:ac:cb": { vendor: "Apple", type: "phone" },
  "e0:b5:2d": { vendor: "Apple", type: "phone" },
  "e0:b9:a5": { vendor: "Apple", type: "phone" },
  "e0:c7:67": { vendor: "Apple", type: "phone" },
  "e4:25:e7": { vendor: "Apple", type: "phone" },
  "e4:8b:7f": { vendor: "Apple", type: "phone" },
  "e4:9a:79": { vendor: "Apple", type: "phone" },
  "e4:ce:8f": { vendor: "Apple", type: "phone" },
  "e4:e4:ab": { vendor: "Apple", type: "phone" },
  "e8:04:0b": { vendor: "Apple", type: "phone" },
  "e8:06:88": { vendor: "Apple", type: "phone" },
  "e8:40:f2": { vendor: "Apple", type: "phone" },
  "e8:80:2e": { vendor: "Apple", type: "phone" },
  "e8:b2:ac": { vendor: "Apple", type: "phone" },
  "ec:35:86": { vendor: "Apple", type: "phone" },
  "ec:85:2f": { vendor: "Apple", type: "phone" },
  "f0:24:75": { vendor: "Apple", type: "phone" },
  "f0:98:9d": { vendor: "Apple", type: "phone" },
  "f0:b4:79": { vendor: "Apple", type: "phone" },
  "f0:c3:71": { vendor: "Apple", type: "phone" },
  "f0:cb:a1": { vendor: "Apple", type: "phone" },
  "f0:d1:a9": { vendor: "Apple", type: "phone" },
  "f0:db:e2": { vendor: "Apple", type: "phone" },
  "f0:db:f8": { vendor: "Apple", type: "phone" },
  "f0:dc:e2": { vendor: "Apple", type: "phone" },
  "f0:f6:1c": { vendor: "Apple", type: "phone" },
  "f4:0f:24": { vendor: "Apple", type: "phone" },
  "f4:1b:a1": { vendor: "Apple", type: "phone" },
  "f4:37:b7": { vendor: "Apple", type: "phone" },
  "f4:5c:89": { vendor: "Apple", type: "phone" },
  "f4:f1:5a": { vendor: "Apple", type: "phone" },
  "f4:f9:51": { vendor: "Apple", type: "phone" },
  "f8:04:2e": { vendor: "Apple", type: "phone" },
  "f8:1e:df": { vendor: "Apple", type: "phone" },
  "f8:27:93": { vendor: "Apple", type: "phone" },
  "f8:95:c7": { vendor: "Apple", type: "phone" },
  "f8:cf:c5": { vendor: "Apple", type: "phone" },
  "fc:18:3c": { vendor: "Apple", type: "phone" },
  "fc:25:3f": { vendor: "Apple", type: "phone" },
  "fc:64:ba": { vendor: "Apple", type: "phone" },
  "fc:e9:98": { vendor: "Apple", type: "phone" },
  // Amazon
  "00:71:47": { vendor: "Amazon", type: "speaker" },
  "00:fc:8b": { vendor: "Amazon", type: "tv" },
  "04:d3:b0": { vendor: "Amazon", type: "speaker" },
  "18:74:2e": { vendor: "Amazon", type: "speaker" },
  "34:d2:70": { vendor: "Amazon", type: "speaker" },
  "38:f7:3d": { vendor: "Amazon", type: "speaker" },
  "44:65:0d": { vendor: "Amazon", type: "speaker" },
  "4c:ef:c0": { vendor: "Amazon", type: "speaker" },
  "50:dc:e7": { vendor: "Amazon", type: "speaker" },
  "68:37:e9": { vendor: "Amazon", type: "speaker" },
  "68:54:fd": { vendor: "Amazon", type: "speaker" },
  "74:75:48": { vendor: "Amazon", type: "speaker" },
  "74:c2:46": { vendor: "Amazon", type: "speaker" },
  "84:d6:d0": { vendor: "Amazon", type: "speaker" },
  "a0:02:dc": { vendor: "Amazon", type: "tv" },
  "ac:63:be": { vendor: "Amazon", type: "speaker" },
  "b0:7d:64": { vendor: "Amazon", type: "speaker" },
  "cc:f4:11": { vendor: "Amazon", type: "speaker" },
  "dc:31:18": { vendor: "Amazon", type: "speaker" },
  "f0:27:2d": { vendor: "Amazon", type: "speaker" },
  "fc:a6:67": { vendor: "Amazon", type: "speaker" },
  "fc:65:de": { vendor: "Amazon", type: "speaker" },
  // Roku
  "b0:a7:37": { vendor: "Roku", type: "tv" },
  "d8:31:34": { vendor: "Roku", type: "tv" },
  "cc:6d:a0": { vendor: "Roku", type: "tv" },
  "ac:3a:7a": { vendor: "Roku", type: "tv" },
  "b8:a1:75": { vendor: "Roku", type: "tv" },
  // Sony
  "00:1d:ba": { vendor: "Sony", type: "tv" },
  "00:23:be": { vendor: "Sony", type: "tv" },
  "30:f9:ed": { vendor: "Sony", type: "tv" },
  "54:42:49": { vendor: "Sony", type: "tv" },
  "ac:9b:0a": { vendor: "Sony", type: "tv" },
  "fc:f1:52": { vendor: "Sony", type: "tv" },
  // Samsung
  "00:12:fb": { vendor: "Samsung", type: "tv" },
  "00:16:32": { vendor: "Samsung", type: "tv" },
  "00:1b:98": { vendor: "Samsung", type: "phone" },
  "20:64:32": { vendor: "Samsung", type: "tv" },
  "40:0e:85": { vendor: "Samsung", type: "phone" },
  "54:88:0e": { vendor: "Samsung", type: "tv" },
  "7c:64:56": { vendor: "Samsung", type: "phone" },
  "e8:50:8b": { vendor: "Samsung", type: "tv" },
  // Google/Nest
  "1c:f2:9a": { vendor: "Google", type: "speaker" },
  "30:fd:38": { vendor: "Google", type: "speaker" },
  "48:d6:d5": { vendor: "Google", type: "speaker" },
  "54:60:09": { vendor: "Google", type: "speaker" },
  "6c:ad:f8": { vendor: "Google", type: "speaker" },
  "a4:77:33": { vendor: "Google", type: "speaker" },
  "b4:f6:2a": { vendor: "Google", type: "speaker" },
  "d4:f5:47": { vendor: "Google", type: "speaker" },
  "f4:f5:d8": { vendor: "Google", type: "speaker" },
};

/**
 * Get vendor info from MAC address
 */
function getMacVendor(mac: string): { vendor: string; type?: string } | null {
  const oui = mac.substring(0, 8).toLowerCase();
  return macVendors[oui] || null;
}

/**
 * Try to get hostname via reverse DNS lookup
 */
async function getHostnameFromIP(ip: string): Promise<string | null> {
  try {
    const hostnames = await dnsReverse(ip);
    return hostnames && hostnames.length > 0 ? hostnames[0] : null;
  } catch (error) {
    // DNS lookup failed, return null
    return null;
  }
}

/**
 * Generate a friendly device name based on available info
 */
function generateDeviceName(
  ip: string,
  mac: string,
  hostname: string | null,
  vendor: { vendor: string; type?: string } | null
): string {
  // If we have a meaningful hostname, use it
  if (hostname && hostname !== ip && !hostname.includes("unknown")) {
    return hostname;
  }

  // If we have vendor info, create a name from it
  if (vendor) {
    const suffix = ip.split(".").pop();
    if (vendor.type === "phone") {
      return `${vendor.vendor} iPhone (${suffix})`;
    } else if (vendor.type === "laptop") {
      return `${vendor.vendor} Mac (${suffix})`;
    } else if (vendor.type === "tv") {
      return `${vendor.vendor} TV (${suffix})`;
    } else if (vendor.type === "speaker") {
      return `${vendor.vendor} Speaker (${suffix})`;
    } else {
      return `${vendor.vendor} Device (${suffix})`;
    }
  }

  // Fallback to IP-based name
  return `Device ${ip.split(".").pop()}`;
}

export interface NetworkDevice {
  id: string;
  name: string;
  ip: string;
  mac: string;
  status: "online" | "offline";
  type: string;
  vendor?: string;
  lastSeen?: Date;
}

export interface NetworkStats {
  connectedDevices: number;
  networkSpeed: number;
  dataUsage: number;
  uptime: string;
}

export interface NetworkActivity {
  id: string;
  device: string;
  action: string;
  timestamp: Date;
}

/**
 * Get network interface statistics
 */
export async function getNetworkStats(): Promise<
  si.Systeminformation.NetworkStatsData[]
> {
  return await si.networkStats();
}

/**
 * Get network interface information
 */
export async function getNetworkInterfaces(): Promise<
  si.Systeminformation.NetworkInterfacesData[]
> {
  return await si.networkInterfaces();
}

/**
 * Get system uptime
 */
export async function getSystemUptime(): Promise<number> {
  const time = await si.time();
  return time.uptime;
}

/**
 * Format uptime in days, hours, minutes
 */
export function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);

  if (days > 0) {
    return `${days}d ${hours}h`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else {
    return `${minutes}m`;
  }
}

/**
 * Scan local network for devices using ARP table
 * This provides a more complete view of all devices on the network
 */
export async function scanNetwork(
  networkPrefix: string = "192.168.1"
): Promise<NetworkDevice[]> {
  const devices: NetworkDevice[] = [];
  const seenMacs = new Set<string>();

  try {
    console.log("🔍 Scanning ARP table for network devices...");

    // Try to get ARP table with timeout
    try {
      const { stdout } = await execAsync("arp -a", {
        timeout: 3000,
        maxBuffer: 1024 * 1024,
      });

      // Parse ARP output
      // Format: hostname (192.168.1.x) at aa:bb:cc:dd:ee:ff [ether] on eth0
      const lines = stdout.split("\n");
      console.log(`📋 Found ${lines.length} ARP entries`);

      for (const line of lines) {
        // Match IP address
        const ipMatch = line.match(/\((\d+\.\d+\.\d+\.\d+)\)/);
        // Match MAC address (various formats)
        const macMatch = line.match(/([0-9a-f]{1,2}[:-]){5}[0-9a-f]{1,2}/i);

        if (ipMatch && macMatch) {
          const ip = ipMatch[1];
          const mac = macMatch[0].toLowerCase();

          // Skip if we've already seen this MAC or if it's incomplete
          if (
            seenMacs.has(mac) ||
            mac === "00:00:00:00:00:00" ||
            line.includes("incomplete")
          ) {
            continue;
          }

          seenMacs.add(mac);

          // Extract hostname if available
          const hostMatch = line.match(/^(\S+)\s+\(/);
          const hostname = hostMatch ? hostMatch[1] : null;

          // Guess device type from hostname or MAC OUI
          let deviceType = "default";
          let deviceName = hostname || `Device-${ip.split(".").pop()}`;

          if (hostname) {
            const lower = hostname.toLowerCase();
            if (lower.includes("iphone") || lower.includes("ipad")) {
              deviceType = "phone";
              deviceName = hostname;
            } else if (
              lower.includes("amazon") ||
              lower.includes("echo") ||
              lower.includes("alexa")
            ) {
              deviceType = "speaker";
              deviceName = hostname;
            } else if (lower.includes("tv") || lower.includes("roku")) {
              deviceType = "tv";
              deviceName = hostname;
            } else if (
              lower.includes("laptop") ||
              lower.includes("macbook") ||
              lower.includes("thinkpad")
            ) {
              deviceType = "laptop";
              deviceName = hostname;
            }
          }

          devices.push({
            id: mac.replace(/[:-]/g, ""),
            name: deviceName,
            ip: ip,
            mac: mac,
            status: "online",
            type: deviceType,
            lastSeen: new Date(),
          });
        }
      }

      console.log(`✅ Found ${devices.length} devices from ARP table`);
    } catch (arpError) {
      console.error(
        "⚠️ ARP scan failed, falling back to interface scan:",
        arpError
      );

      // Fallback to network interfaces
      const interfaces = await getNetworkInterfaces();

      for (const iface of interfaces) {
        if (
          iface.ip4 &&
          iface.ip4 !== "127.0.0.1" &&
          iface.mac &&
          iface.mac !== "00:00:00:00:00:00" &&
          !seenMacs.has(iface.mac)
        ) {
          seenMacs.add(iface.mac);
          devices.push({
            id: iface.mac.replace(/:/g, ""),
            name: iface.iface || `Device-${iface.ip4.split(".").pop()}`,
            ip: iface.ip4,
            mac: iface.mac,
            status: "online",
            type:
              iface.iface.toLowerCase().includes("wlan") ||
              iface.iface.toLowerCase().includes("wi")
                ? "laptop"
                : "default",
            lastSeen: new Date(),
          });
        }
      }

      console.log(`✅ Fallback: Created ${devices.length} device entries`);
    }
  } catch (error) {
    console.error("❌ Network scan error:", error);
  }

  return devices;
}

/**
 * Get ARP table from system
 */
async function getArpTable(): Promise<Array<{ ip: string; mac: string }>> {
  try {
    const { stdout } = await execAsync("arp -a");
    const entries: Array<{ ip: string; mac: string }> = [];

    // Parse ARP output
    const lines = stdout.split("\n");
    for (const line of lines) {
      // Match IP and MAC address patterns
      const ipMatch = line.match(/\((\d+\.\d+\.\d+\.\d+)\)/);
      const macMatch = line.match(
        /([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})/
      );

      if (ipMatch && macMatch) {
        entries.push({
          ip: ipMatch[1],
          mac: macMatch[1].toLowerCase(),
        });
      }
    }

    return entries;
  } catch (error) {
    console.error("Failed to get ARP table:", error);
    return [];
  }
}

/**
 * Attempt to get hostname for IP address
 */
async function getDeviceHostname(ip: string): Promise<string | null> {
  return new Promise((resolve) => {
    arp.getMAC(ip, (err, mac) => {
      if (err) {
        resolve(null);
      } else {
        // Try reverse DNS lookup
        exec(`nslookup ${ip}`, (error, stdout) => {
          if (error) {
            resolve(null);
          } else {
            const nameMatch = stdout.match(/name = (.+)/);
            resolve(nameMatch ? nameMatch[1].trim() : null);
          }
        });
      }
    });
  });
}

/**
 * Guess device type based on MAC address OUI
 */
function guessDeviceType(mac: string): string {
  const oui = mac.substring(0, 8).toLowerCase();

  // Common device type patterns (partial list)
  const patterns: Record<string, string> = {
    // Apple devices
    "00:03:93": "mobile",
    "00:0a:95": "mobile",
    "00:1b:63": "mobile",
    "ac:de:48": "mobile",
    "f0:18:98": "laptop",

    // Samsung
    "00:12:fb": "mobile",
    "00:1d:25": "tv",

    // Google/Nest
    "54:60:09": "iot",
    "6c:ad:f8": "iot",

    // Raspberry Pi
    "b8:27:eb": "iot",
    "dc:a6:32": "iot",
  };

  return patterns[oui] || "default";
}

/**
 * Get MAC vendor from OUI (simplified - in production use an API)
 */
async function getMacVendor(mac: string): Promise<string | undefined> {
  const oui = mac.substring(0, 8).toLowerCase();

  // Common vendors (partial list - in production, use IEEE OUI database or API)
  const vendors: Record<string, string> = {
    "00:03:93": "Apple",
    "00:0a:95": "Apple",
    "00:1b:63": "Apple",
    "ac:de:48": "Apple",
    "f0:18:98": "Apple",
    "00:12:fb": "Samsung",
    "00:1d:25": "Samsung",
    "54:60:09": "Google",
    "6c:ad:f8": "Google",
    "b8:27:eb": "Raspberry Pi Foundation",
    "dc:a6:32": "Raspberry Pi Trading",
  };

  return vendors[oui];
}

/**
 * Calculate network speed based on interface stats
 */
export async function calculateNetworkSpeed(): Promise<number> {
  const stats = await getNetworkStats();

  // Get primary interface (usually the one with most traffic)
  const primaryInterface = stats.reduce((prev, current) =>
    prev.rx_bytes + prev.tx_bytes > current.rx_bytes + current.tx_bytes
      ? prev
      : current
  );

  // Convert bytes/sec to Mbps
  const speedMbps =
    ((primaryInterface.rx_sec + primaryInterface.tx_sec) * 8) / 1000000;

  return Math.round(speedMbps);
}

/**
 * Calculate total data usage
 */
export async function calculateDataUsage(): Promise<number> {
  const stats = await getNetworkStats();

  const totalBytes = stats.reduce(
    (sum, iface) => sum + iface.rx_bytes + iface.tx_bytes,
    0
  );

  // Convert to GB
  return Math.round((totalBytes / 1073741824) * 10) / 10;
}

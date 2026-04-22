"""
Indoor Floor/Path Segmentation using LRASPP-MobileNet v3
Optimized for speed - runs on GPU if available, CPU fallback
"""
import cv2
import numpy as np
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import lraspp_mobilenet_v3_large

class FloorSegmenter:
    """
    Fast indoor floor/path segmentation.
    Uses LRASPP-MobileNet v3 (fastest segmentation model in torchvision).
    Cityscapes classes: road=0, sidewalk=1, terrain=9 are walkable.
    """

    WALKABLE = {0, 1, 9}   # road, sidewalk, terrain
    OBSTACLE  = {11, 12, 13, 14, 15, 16, 17, 18}  # person, rider, vehicles

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model  = None
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406],
                        std =[0.229, 0.224, 0.225])
        ])
        # Run at reduced resolution for speed
        self.infer_w = 320
        self.infer_h = 240

    def initialize(self) -> bool:
        try:
            print("🗺️  Loading LRASPP-MobileNet v3 segmentation model...")
            self.model = lraspp_mobilenet_v3_large(weights="DEFAULT")
            self.model.to(self.device).eval()
            print(f"✅ Segmentation model loaded on {self.device}")
            return True
        except Exception as e:
            print(f"⚠️  Segmentation model failed: {e}")
            return False

    def segment(self, frame: np.ndarray) -> np.ndarray:
        """
        Returns segmentation map (H x W) with class indices.
        Runs at reduced resolution for speed, resizes back.
        """
        if self.model is None:
            return np.zeros(frame.shape[:2], dtype=np.uint8)

        try:
            orig_h, orig_w = frame.shape[:2]
            small = cv2.resize(frame, (self.infer_w, self.infer_h))
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

            inp = self.transform(rgb).unsqueeze(0).to(self.device)
            with torch.no_grad():
                out = self.model(inp)["out"][0]

            seg = out.argmax(0).cpu().numpy().astype(np.uint8)
            seg = cv2.resize(seg, (orig_w, orig_h), interpolation=cv2.INTER_NEAREST)
            return seg

        except Exception:
            return np.zeros(frame.shape[:2], dtype=np.uint8)

    def get_floor_mask(self, seg: np.ndarray) -> np.ndarray:
        """Binary mask: 255 = walkable floor, 0 = not walkable"""
        mask = np.zeros(seg.shape, dtype=np.uint8)
        for c in self.WALKABLE:
            mask[seg == c] = 255
        # Morphological cleanup
        k = np.ones((7, 7), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k)
        return mask

    def get_path_direction(self, mask: np.ndarray) -> dict:
        """Returns walkable % for left / center / right in bottom 60% of frame"""
        h, w = mask.shape
        roi  = mask[int(h * 0.4):, :]
        l    = roi[:, :w//3]
        c    = roi[:, w//3:2*w//3]
        r    = roi[:, 2*w//3:]
        pct  = lambda x: float(np.sum(x > 0)) / x.size * 100
        return {"left": pct(l), "center": pct(c), "right": pct(r)}

    def get_guidance(self, d: dict) -> tuple:
        """Returns (text, bgr_color)"""
        if d["center"] > 40:
            return "Path CLEAR ahead", (0, 255, 0)
        elif d["left"] > d["right"] and d["left"] > 25:
            return "Move LEFT", (0, 255, 255)
        elif d["right"] > d["left"] and d["right"] > 25:
            return "Move RIGHT", (0, 255, 255)
        else:
            return "Path BLOCKED", (0, 0, 255)

    def build_seg_panel(self, frame: np.ndarray, mask: np.ndarray,
                        direction: dict, guidance: str,
                        guidance_color: tuple) -> np.ndarray:
        """Build a rich segmentation visualization panel"""
        h, w = frame.shape[:2]

        # Green overlay on walkable floor
        overlay = frame.copy()
        overlay[mask > 0] = (0, 200, 80)
        panel = cv2.addWeighted(frame, 0.55, overlay, 0.45, 0)

        # Title bar
        cv2.rectangle(panel, (0, 0), (w, 36), (20, 20, 20), -1)
        cv2.putText(panel, "FLOOR PATH  |  LRASPP-MobileNet v3",
                    (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        # Direction bars (bottom area)
        bar_y = h - 70
        bar_h = 18
        sections = [("L", direction["left"],  10),
                    ("C", direction["center"], w//3 + 10),
                    ("R", direction["right"],  2*w//3 + 10)]
        for label, pct, x in sections:
            bar_len = int((w//3 - 20) * min(pct, 100) / 100)
            col = (0, 255, 0) if pct > 40 else (0, 165, 255) if pct > 20 else (0, 0, 255)
            cv2.rectangle(panel, (x, bar_y), (x + bar_len, bar_y + bar_h), col, -1)
            cv2.rectangle(panel, (x, bar_y), (x + w//3 - 20, bar_y + bar_h), (180,180,180), 1)
            cv2.putText(panel, f"{label}:{pct:.0f}%", (x + 2, bar_y + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)

        # Guidance text
        cv2.putText(panel, guidance, (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, guidance_color, 2)

        return panel

from math import sqrt


class Point:
    def __init__(self, name: str, bitrate: float, encoding_time: float):
        self.name = name
        self.bitrate = bitrate
        self.encoding_time = encoding_time

    def distance_to_point(self, other_point) -> float:
        return sqrt(
            (self.bitrate - other_point.bitrate) ** 2
            + (self.encoding_time - other_point.encoding_time) ** 2
        )

    def closest_point(self, other_points: list) -> tuple[int, float] | None:
        idx_and_distances: list[tuple[int, float]] = [
            (idx, self.distance_to_point(op)) for idx, op in enumerate(other_points)
        ]
        idx_and_distances.sort(key=lambda tpl: tpl[1])
        return next(iter(idx_and_distances), None)


av1: list[tuple[str, float, float]] = [
    ("AV1 - preset 5 - CRF 38", 8813.75, 204.17188),
    ("AV1 - preset 5 - CRF 5", 85448.73, 300.06615),
    ("AV1 - preset 4 - CRF 38", 8417.78, 418.90027),
    ("AV1 - preset 4 - CRF 9", 58622.96, 724.54378),
    ("AV1 - preset 5 - CRF 63", 937.51, 108.87405),
    ("AV1 - preset 5 - CRF 54", 3128.82, 156.49183),
    ("AV1 - preset 5 - CRF 50", 4101.86, 160.49895),
    ("AV1 - preset 5 - CRF 46", 5370.92, 169.87308),
    ("AV1 - preset 5 - CRF 42", 6739.08, 179.08629),
    ("AV1 - preset 5 - CRF 34", 11438.6, 232.92423),
    ("AV1 - preset 5 - CRF 29", 15544.78, 256.55932),
    ("AV1 - preset 5 - CRF 25", 19844.07, 273.12577),
    ("AV1 - preset 5 - CRF 21", 25507.02, 289.04398),
    ("AV1 - preset 4 - CRF 21", 25543.86, 865.3031),
    ("AV1 - preset 4 - CRF 17", 30529.63, 793.20628),
    ("AV1 - preset 4 - CRF 13", 40215.03, 771.76168),
    ("AV1 - preset 4 - CRF 5", 82595.29, 639.46189),
    ("AV1 - preset 4 - CRF 1", 132807.17, 650.36067),
]

hevc: list[tuple[str, float, float]] = [
    ("HEVC - preset slower - CRF 17", 26717.42, 785.65823),
    ("HEVC - preset slower - CRF 13", 46349.21, 944.8234),
    ("HEVC - preset slower - CRF 10", 72506.95, 1061.7744),
    ("HEVC - preset slow - CRF 44", 760.5, 84.84763),
    ("HEVC - preset slow - CRF 23", 14056.46, 268.20159),
    ("HEVC - preset slow - CRF 0", 195605.0, 386.52514),
    ("HEVC - preset slower - CRF 27", 7999.91, 820.74185),
    ("HEVC - preset slower - CRF 3", 144956.35, 1277.60172),
    ("HEVC - preset slow - CRF 51", 741.17, 49.41322),
    ("HEVC - preset slow - CRF 40", 1380.6, 121.683),
    ("HEVC - preset slow - CRF 37", 2202.01, 142.07787),
    ("HEVC - preset slow - CRF 34", 3395.97, 312.92876),
    ("HEVC - preset slow - CRF 30", 5846.32, 270.1549),
    ("HEVC - preset slow - CRF 27", 8618.76, 232.50837),
    ("HEVC - preset slow - CRF 20", 20034.05, 304.84992),
    ("HEVC - preset slow - CRF 17", 29014.39, 278.00438),
    ("HEVC - preset slow - CRF 13", 50912.89, 317.71699),
    ("HEVC - preset slow - CRF 10", 80234.16, 353.16076),
    ("HEVC - preset slow - CRF 6", 122594.21, 396.23584),
    ("HEVC - preset slow - CRF 3", 153764.87, 412.99358),
    ("HEVC - preset slower - CRF 51", 663.73, 171.17184),
    ("HEVC - preset slower - CRF 44", 705.74, 199.33278),
    ("HEVC - preset slower - CRF 40", 1299.84, 272.8478),
    ("HEVC - preset slower - CRF 37", 2079.83, 331.67739),
    ("HEVC - preset slower - CRF 34", 3199.76, 393.60414),
    ("HEVC - preset slower - CRF 30", 5451.24, 852.84733),
    ("HEVC - preset slower - CRF 23", 13018.12, 630.12235),
    ("HEVC - preset slower - CRF 20", 18518.21, 697.07189),
    ("HEVC - preset slower - CRF 6", 113555.0, 1175.88587),
    ("HEVC - preset slower - CRF 0", 187578.91, 1524.80378),
]


def get_closest(point_count: int) -> list[tuple[Point, Point]]:
    av1_points: list[Point] = [Point(tpl[0], tpl[1], tpl[2]) for tpl in av1]
    hevc_points: list[Point] = [Point(tpl[0], tpl[1], tpl[2]) for tpl in hevc]
    chosen_points: list[tuple[Point, Point]] = []
    while len(chosen_points) < point_count and av1_points:
        distances: list[int, int, float] = []
        for i, p in enumerate(av1_points):
            distances.append((i, *p.closest_point(hevc_points)))
        av1_idx, hevc_idx, _distance = next(
            iter(sorted(distances, key=lambda tpl: tpl[2]))
        )
        chosen_points.append((av1_points.pop(av1_idx), hevc_points.pop(hevc_idx)))
    return chosen_points

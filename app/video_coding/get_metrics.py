from video_coding.entities.models import EncodedVideoFile, FilterResults, OriginalVideoFile


def get_ovf_metrics(ovf: OriginalVideoFile):
    evfs = list(ovf.encoded_video_files.all())
    metrics = {p: [] for p in set([evf.name.split(" ")[0] for evf in evfs])}
    for evf in evfs:
        metrics[evf.name.split(" ")[0]].append(get_evf_metrics(evf))
    for codec, codec_metrics in metrics.items():
        codec_metrics.sort(key=lambda k: k['bitrate'])
        metrics[codec] = codec_metrics
    return metrics


def get_evf_metrics(evf: EncodedVideoFile) -> dict:
    results: list[FilterResults] = list(evf.decoded_video_file.filter_results.all())
    metrics = {
        'bitrate': evf.bitrate,
        'encoding_time': evf.encoding_time,
    }
    keywords: dict = {
        'PSNR': 'average:',
        'VMAF': 'VMAF score:',
    }
    for r in results:
        out: str = r.output
        for metric_name, kw in keywords.items():
            if kw in out:
                idx: int = out.find(kw)
                metrics[metric_name] = out[idx + len(kw): ].split()[0]
    return metrics


def get_psnr_bitrate_values(ovf_metrics: dict, keys=None) -> dict:
    keys = keys if keys else ['bitrate', 'encoding_time', 'PSNR']
    metrics: dict = {codec: dict() for codec in ovf_metrics}
    for codec, evf_metrics in ovf_metrics.items():
        aggregated_metrics = {k: [] for k in keys}
        for evfm in evf_metrics:
            for k in keys:
                aggregated_metrics[k].append(evfm[k])
        metrics[codec] = aggregated_metrics
    return metrics

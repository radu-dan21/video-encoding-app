from operator import itemgetter


def vf_post_save_hook(**kwargs):
    try:
        created, instance = itemgetter("created", "instance")(kwargs)
    except KeyError:
        return

    if not created:
        return
    instance.create_folder_structure()


def vf_post_delete_hook(**kwargs):
    instance = kwargs.get("instance")
    if instance:
        instance.remove_folder_structure()

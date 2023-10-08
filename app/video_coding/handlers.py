from operator import itemgetter


def vf_post_save_hook(**kwargs):
    """
    Post save hook for subclasses of BaseVideoFile
    Should create the internal folder structure when an instance is created
    :param kwargs: post save hook specific kwargs
    """
    try:
        created, instance = itemgetter("created", "instance")(kwargs)
    except KeyError:
        return

    if not created:
        return
    instance.create_folder_structure()


def vf_post_delete_hook(**kwargs):
    """
    Post delete hook for subclasses of BaseVideoFile
    Should delete the internal folder structure when an instance is deleted
    :param kwargs: post delete hook specific kwargs
    """
    instance = kwargs.get("instance")
    if instance:
        instance.remove_folder_structure(

            
        )

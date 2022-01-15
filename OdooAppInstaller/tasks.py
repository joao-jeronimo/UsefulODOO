from invoke import task

@task
def install_release(c, release_num):
    c.sudo("./Install.bash")

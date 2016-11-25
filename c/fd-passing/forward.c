#include <errno.h>
#include <error.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>

#define CHANNEL_PATH "/tmp/socketpassing.sock"

int send_fd(int sockfd, int fd)
{
    int ret;
    char            buf[1];
    struct iovec    iov;
    struct msghdr   msg;
    struct cmsghdr  *cmsg;
    union {
        char buf[CMSG_SPACE(sizeof(fd))];
        struct cmsghdr align;
    } ancillarybuf;

    memset(&iov, 0, sizeof(iov));
    iov.iov_base = buf;
    iov.iov_len = sizeof(buf);

    memset(&msg, 0, sizeof(msg));
    msg.msg_control = &ancillarybuf.buf;
    msg.msg_controllen = sizeof(ancillarybuf.buf);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    /*
     * Setup Control MSG Header for fd-passing and set fd into it
     */
    cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET; // For historical reasons, used instead of AF_UNIX
    cmsg->cmsg_type = SCM_RIGHTS; // The one flag to set for fd-passing
    cmsg->cmsg_len = CMSG_LEN(sizeof(fd));
    *((int*)CMSG_DATA(cmsg)) = fd;

again:
    ret = sendmsg(sockfd, &msg, 0);
    if (ret == -1)
    {
        if (errno == EINTR || errno == EAGAIN)
            goto again;
        printf("Could not send msg to unix socket: %s\n", strerror(errno));
        goto end;
    }

    ret = 0;

end:
    if (close(fd) != 0)
        printf("Could not close fd: %s\n", strerror(errno));

    return ret;
}

int main(int ac, char *av[])
{
    struct sockaddr_un addr;
    char *filename = av[1];
    int fd, sockfd = -1;
    int ret;

    if (ac != 2)
    {
        printf("Usage: %s filepath\n", av[0]);
        ret = 1;
        goto end;
    }

    fd = open(filename, O_RDONLY);
    if (fd == -1)
    {
        printf("Could not open file: %s\n", strerror(errno));
        ret = 1;
        goto end;
    }

    sockfd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (sockfd == -1)
    {
        printf("Could not create socket: %s\n", strerror(errno));
        ret = 1;
        goto end;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, CHANNEL_PATH, sizeof(addr.sun_path)-1);

    ret = connect(sockfd, (struct sockaddr*)&addr, sizeof(addr));
    if (ret != 0)
    {
        printf("Could not connect to unix socket %s: %s\n", CHANNEL_PATH, strerror(errno));
        ret = 1;
        goto end;
    }

    ret = send_fd(sockfd, fd);
    if (ret != 0)
    {
    }





    ret = 0;

end:
    ret = shutdown(sockfd, SHUT_RDWR); 
    if (ret == -1)
        printf("Could not shutdown socket properly: %s\n", strerror(errno));
    ret = close(sockfd);
    if (ret == -1)
        printf("Could not close socket properly: %s\n", strerror(errno));
    
    return ret;
}

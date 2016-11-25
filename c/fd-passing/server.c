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

int recv_fd(int clientsock)
{
    int rc, datafd = -1;
    char            buf[1];
    struct iovec    iov;
    struct msghdr   msg;
    struct cmsghdr  *cmsg;
    union {
        char buf[CMSG_SPACE(sizeof(datafd))];
        struct cmsghdr align;
    } ancillarybuf;

    memset(&iov, 0, sizeof(iov));
    iov.iov_base = buf;
    iov.iov_len = 1;

    memset(&msg, 0, sizeof(msg));
    msg.msg_control = &ancillarybuf.buf;
    msg.msg_controllen = sizeof(ancillarybuf.buf);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    rc = recvmsg(clientsock, &msg, 0);
    if (rc <= 0)
    {
        printf("Could not receive any message: rc=%i, %s\n", rc, strerror(errno));
        goto end;
    }

    printf("Got a message, rc=%i, first cmsg=%p\n", rc, CMSG_FIRSTHDR(&msg));
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg))
    {
        printf("One cmsg: level=%i, type=%i, len=%i (expected %i, %i %i)...\n",
               cmsg->cmsg_level, cmsg->cmsg_type, cmsg->cmsg_len,
               SOL_SOCKET, SCM_RIGHTS, CMSG_LEN(sizeof(datafd)));
        if (cmsg->cmsg_level == SOL_SOCKET
            && cmsg->cmsg_type == SCM_RIGHTS
            && cmsg->cmsg_len == CMSG_LEN(sizeof(datafd)))
        {
            int i, j, tmpfd = -1;

            /*
             * We only accept one file descriptor.  Due to C
             * padding rules, our control buffer might contain
             * more than one fd, and we must close them.
             */
            j = ((char *)cmsg + cmsg->cmsg_len -
                (char *)CMSG_DATA(cmsg)) / sizeof(int);
            for (int i = 0; i < j; i++)
            {
                tmpfd = ((int *)CMSG_DATA(cmsg))[i];
                if (datafd == -1)
                    datafd = tmpfd;
                else
                    close(tmpfd);
            }
        }
        else
            printf("Got another type of cmsg: level=%i, type=%i\n", cmsg->cmsg_level, cmsg->cmsg_type);
    }

end:
    return datafd;
}

int read_file(int fd)
{
    int rc;
    char buf[4096];

    do {
        rc = read(fd, buf, sizeof(buf));
        if (rc < 0) {
            if (errno == EAGAIN || errno == EINTR)
                continue ;
            printf("Could not read data from received fd: %s\n", strerror(errno));
            return 1;
        }
        (void)write(1, buf, rc);
    } while (rc > 0);

    return 0;
}

int main(int argc, char *argv[])
{
    int ret;
    struct sockaddr_un addr;
    int sockfd = -1, clientsock, rc, datafd = -1;

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
    ret = bind(sockfd, (struct sockaddr*)&addr, sizeof(addr)); 
    if (ret == -1)
    {
        printf("Could not bind server socket: %s\n", strerror(errno));
        ret = 1;
        goto end;
    }

    ret = listen(sockfd, 5);
    if (ret == -1)
    {
        printf("Could not listen to server socket: %s\n", strerror(errno));
        ret = 1;
        goto end;
    }

    do {
        clientsock = accept(sockfd, NULL, NULL);
        if (clientsock == -1) {
            printf("Could not accept: %s\n", strerror(errno));
            ret = 1;
            goto end;
        }

        datafd = recv_fd(clientsock);
        if (datafd == -1)
            printf("Could not receive FD :(.\n");
        else
        {
            if (read_file(datafd) != 0)
                printf("Could not read transmitted file :(.\n");
            printf("\n");
            if (close(datafd) == -1)
                printf("Could not close datafd properly?\n");
            datafd = -1;
        }

        close(clientsock);
        clientsock = -1;
    } while (clientsock != -1);

end:
    if (sockfd != -1 && close(sockfd) == -1)
        printf("Could not close server socket: %s\n", strerror(errno));
    if (sockfd != -1 && unlink(CHANNEL_PATH) == -1)
        printf("Could not unlink unix socket: %s\n", strerror(errno));

    return ret;
}

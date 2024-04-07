## Set tup an EC2 instance for Rancher

1. AWS 로그인 후에 EC2-인스턴스에서 인스턴스 시작을 누른다.

2. 애플리케이션 및 OS 이미지로 `Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type(64비트 x86)`을 선택한다.

3. Rancer가 2GB의 메모리를 필요로 하기에 인스턴스 유형으로 `t2.small`을 선택한다.

4. 새 키 페어를 적절한 이름으로 생성하고, 저장된 키를 안전한 곳에 보관한다.

5. 네트워크 설정에서 HTTP와 HTTPS 트래픽 허용을 선택한다.

6. 인스턴스 시작

7. 작업-연결에서 브라우저 기반으로 인스턴스에 연결한다.

8. 다음의 명령어들을 순서대로 입력한다.

```bash
# update installed packages and package cache
sudo yum update -y

# install docker community edition package
sudo amazon-linux-extras install docker

# start docker service
sudo service docker start

# add 'ec2-user' to the docker group so we can execute docker commands without using sudo
sudo usermod -a -G docker ec2-user

# 이후에 인스턴스 종료 후, 재시작으로 new docker group permission 적용

# start rancher
docker run -d --restart=unless-stopped --name rancher --hostname rancher -p 80:80 -p 443:443 rancher/rancher:v2.3.2
```

9. public ip에 접속

- 경고창이 뜨는데 그대로 접속한다.

### Troubleshooting of this part.

1. 아래 단계에서 Rancher를 통해 EKS 클러스터를 생성할 때 `Error creating cluster: InvalidParameterException: unsupported Kubernetes version status code: 400, request id: d24344a8-25ca-4af6-840b-ab37b7090d1b` 에러가 뜬다.

> Rancher 버전이 너무 오래돼서 예전 쿠버네티스 버전만 서포트해서 생긴 에러이다.
> 위의 ec2 인스턴스 내에서 실행하는 start rancher 명령어 부분을 다음과 같이 변경한다.

```bash
docker run --privileged -d --restart=unless-stopped --name udemy-rancher --hostname rancher -p 80:80 -p 443:443 rancher/rancher:stable
```

이후에 public ip에 접속하면 이전에는 없던 인증 절차가 있다.

```bash
docker logs $(docker ps -aqf "name=udemy-rancher") 2>&1 | grep "Bootstrap Password:"
```

를 인스턴스 터미널에 실행하는 것을 통해 인증 비밀번호를 알아오고 이를 입력한다.

> 이후에 개인 비밀번호를 설정한다.

**이 방식으로 하면 클러스터가 자동으로 설치되어 있다.**

## Create an IAM User with permission

- it is required by rancher to set up an EKS cluster.

1. AWS에서 IAM service에서 사용자 탭에서 사용자 생성을 클릭한다.
2. 사용자 이름 지정. 예시: `udemy-airflow-user`
3. 그룹으로 권한 설정을 해도 되지만 지금은 간단하게 '직접 정책 설정' 클릭해서 `AdministratorAccess` 부여
4. 사용자 생성
5. `udemy-airflow-user` 에서 액세스 키를 원하는 이름으로 `AWS 컴퓨팅 서비스에서 실행되는 애플리케이션` 옵션으로 생성 후에 저장하여 안전한 곳에 보관

## Create an ECR repository

- ECR repository to store, manage and deploy docker container images
- It is good for CI/CD

1. AWS에서 ECR에서 리포지토리 생성 '시작하기' 클릭
2. Private으로 원하는 이름의 리포지토리 생성: `udemy-airflow`
3. docker image를 이곳에 푸시하기 위해서는 AWS CLI가 필요하다.

```bash
brew install awscli

which aws

aws --version
```

4. aws 자격증명

```bash
aws configure
```

후에 IAM user 생성 과정에서 만든 액세스 키의 ID와 secre을 입력한다.
region은 `ap-northeast-2`이다.

4. 생성한 리포지토리에 들어가면 `푸시 명령 보기`가 있다. 그곳에 있는 명령어들을 순서대로 입력한다. (docker build를 위해서 Dockerfile이 있는 곳에서 명령어를 실행한다.)

- tag에서 latest 대신 `v1.0`과 같이 특정 버전을 쓰자.

### Troubleshooting of this process

1. python image version에 따른 에러가 발생했다.

Docker file의 파이썬 버전을

```bash
FROM python:3.7-slim-stretch
```

에서

```bash
FROM python:3.7-slim-buster
```

으로 변경하였다.

2. Flask-OpenId 버전

requirements-python3.7.txt에서

```bash
Flask-OpenID==1.2.5
```

에서

```bash
Flask-OpenID==1.3.0
```

으로 변경하여 dependency에 따른 에러를 해결하였다.

## Create an EKS cluster with Rancher

1. Rancher에서 `Add Cluster` 클릭
2. Amazon EKS 선택
3. Cluster Name으로 원하는 것 입력: `udemyAirflowEKSCluster`
4. Account Access에서 IAM User에 맞는 region, Access Key, Secret Key 입력.
5. 나머지는 default로 생성
6. node group name으로 `udemy-airflow`
   - 이것이 무엇인지 찾아볼 필요가 있다.

## How to access applications from the outside

- service, load balancer, ingress(어렵지만 이 방법이 recommended)

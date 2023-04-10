from pulumi import export
import pulumi_aws as aws

vpc = aws.ec2.Vpc(
	"ec2-vpc",
	cidr_block="10.0.0.0/16"
)

public_subnet = aws.ec2.Subnet(
	"ec2-public-subnet",
	cidr_block="10.0.101.0/24",
	tags={
		"Name": "ec2-public"
	},
	vpc_id=vpc.id
)

igw = aws.ec2.InternetGateway(
	"ec2-igw",
	vpc_id=vpc.id,
)

route_table = aws.ec2.RouteTable(
	"ec2-route-table",
	vpc_id=vpc.id,
	routes=[
		{
			"cidr_block": "0.0.0.0/0",
			"gateway_id": igw.id
		}
	]
)

rt_assoc = aws.ec2.RouteTableAssociation(
	"ec2-rta",
	route_table_id=route_table.id,
	subnet_id=public_subnet.id
)


sg = aws.ec2.SecurityGroup(
	"ec2-http-sg",
	description="Allow HTTP traffic to EC2 instance",
	ingress=[{
		"protocol": "tcp",
		"from_port": 80,
		"to_port": 80,
		"cidr_blocks": ["0.0.0.0/0"],
        #ssh ports
        "protocol": "tcp",
        "from_port": 22,
        "to_port": 22,
        "cidr_blocks": ["0.0.0.0/0"],
	}],
    vpc_id=vpc.id,
)

ami = aws.ec2.get_ami(
	most_recent="true",
	owners=["amazon"],
	filters=[{"name": "name", "values": ["amzn-ami-hvm-*"]}]
)
#keypair
keypair = aws.ec2.KeyPair("keypair", public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDdVUGE18EZ9KBGrOI/Lbp/tPepve2QxuFDt20yUvDzTMhxUCkqdng2PgVT6g21R9SESQrR5l0oXgKrzV6OHEuJp0aFbsKeQP9h0fU23KXBXb6Vaix2OYz0PpRCthwpKc6g577Gb/e5d468ixU74hjbpE69EBTq4LDoZC1qz4TLImjY9fIqC3BX4jRPiLh345+/RyiKM64l5hw3chLIic+RZ0XeytH0tgB7/bMOWyyZ2HR4hLd94AwaEtBlTBKVcFtVFQS+gMSSBI3H+SIHS2BNMZ+nrSDHZrX7zAuehu5MI4ibUG1m7UzlRDV6Z6cbvCgWGUGAYrTdGmw7eNWEfnr06nlqVdIN7RLvRKN88FDUV2PDkd/HPrz99iK14ABXkZUQdcSH0m1817dB7UpgJkq9InPY6Pi7fQ2Lh4HoJw/j2iAVBs6j+njXdP3BfjQSkbytW3HWoYLEB5xvJngfjEFIRMt0fVBVysJyUWNQNFmAQwCmxgu1S2Rjz/EGQrwJuCc= cwills@Cs-MacBook-Pro.loca")

user_data = """
#!/bin/bash
echo "Hello, world!" > index.html
nohup python -m SimpleHTTPServer 80 &
"""

ec2_instance = aws.ec2.Instance(
	"ec2-tutorial",
	instance_type="t2.micro",
	vpc_security_group_ids=[sg.id],
	ami=ami.id,
    key_name=keypair.key_name,
	user_data=user_data,
    subnet_id=public_subnet.id,
    associate_public_ip_address=True,
)


export("ec2-public-ip", ec2_instance.public_ip)

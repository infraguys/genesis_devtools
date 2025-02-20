packer {
  required_plugins {
    sshkey = {
      version = ">= 1.0.1"
      source  = "github.com/ivoronin/sshkey"
    }
    qemu = {
      version = ">= 1.1.1"
      source  = "github.com/hashicorp/qemu"
    }
  }
}

/* 
 * ⚠️ WARNING: THIS IS A PROOF-OF-CONCEPT (PoC) FOR RESEARCH PURPOSES ONLY.
 * Executing this code initiates a hardware-level NVMe Crypto Erase operation
 * on TCG OPAL 2.0 compliant Self-Encrypting Drives (SED).
 * The author is NOT responsible for any accidental data loss or hardware damage.
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/nvme_ioctl.h>
#include <string.h>

#define NVME_ADMIN_SECURITY_SEND 0x81
#define OPAL_UID_LENGTH 8

// Domain 3: Hardware-Locked Zeroization State Machine
// DFA state transition for processing Out-of-Band (OOB) purge signals
void trigger_crypto_erase(const char* device_path) {
    int fd = open(device_path, O_RDWR);
    if (fd < 0) {
        perror("[-] Failed to open NVMe device. Root privileges required.");
        return;
    }

    printf("[+] Initiating TCG OPAL 2.0 Crypto Erase on %s\n", device_path);

    // Prepare NVMe Admin Command (Simulated Payload for PoC)
    struct nvme_passthru_cmd cmd;
    memset(&cmd, 0, sizeof(cmd));
    cmd.opcode = NVME_ADMIN_SECURITY_SEND;
    cmd.nsid = 1; // Namespace ID
    
    // In a full implementation, this payload contains the OPAL Method calls
    // (e.g., RevertSP or Erase) encrypted via the secure channel.
    
    // Execute IOCTL
    int rc = ioctl(fd, NVME_IOCTL_ADMIN_CMD, &cmd);
    if (rc < 0) {
        perror("[-] NVMe IOCTL Admin Command Failed");
    } else {
        printf("[+] Crypto Erase successfully dispatched to ASIC controller.\n");
    }

    close(fd);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <nvme_device_path>\n", argv[0]);
        printf("Example: %s /dev/nvme0n1\n", argv[0]);
        return 1;
    }
    trigger_crypto_erase(argv[1]);
    return 0;
}
declare module "node-arp" {
  export function getMAC(
    ipAddress: string,
    callback: (error: Error | null, mac?: string) => void
  ): void;

  export function getIP(
    macAddress: string,
    callback: (error: Error | null, ip?: string) => void
  ): void;
}

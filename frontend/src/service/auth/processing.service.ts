export class ProcessingService {
  private isProcessing = false;

  get value() {
    return this.isProcessing;
  }

  start(): boolean {
    if (this.isProcessing) return false;
    this.isProcessing = true;
    return true;
  }

  stop(): void {
    this.isProcessing = false;
  }
}
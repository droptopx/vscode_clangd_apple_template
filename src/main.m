@import Cocoa;

@interface AppDelegate : NSObject <NSApplicationDelegate, NSWindowDelegate>

@property(nonatomic, strong) NSWindow *window;

@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
  // Create a window
  self.window = [[NSWindow alloc]
      initWithContentRect:NSMakeRect(100, 100, 400, 300)
                styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable |
                           NSWindowStyleMaskResizable)
                  backing:NSBackingStoreBuffered
                    defer:NO];

  [self.window setTitle:@"Wait for Close Example"];
  [self.window setDelegate:self];

  // Add some content to the window (optional)
  NSTextField *textField =
      [[NSTextField alloc] initWithFrame:NSMakeRect(50, 150, 300, 30)];
  [textField setStringValue:@"Close this window to continue..."];
  [textField setEditable:NO];
  [textField setBezeled:NO];
  [textField setDrawsBackground:NO];

  [[self.window contentView] addSubview:textField];

  // Show the window
  [self.window makeKeyAndOrderFront:self];
}

- (void)windowWillClose:(NSNotification *)notification {
  // The window is about to close, stop the application
  [NSApp terminate:self];
}

@end

int main(int argc, const char *argv[]) {
  @autoreleasepool {
    NSApplication *application = [NSApplication sharedApplication];
    AppDelegate *appDelegate = [[AppDelegate alloc] init];
    [application setDelegate:appDelegate];
    [application run];
  }
  return 0;
}

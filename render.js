/**
 * BEAT THE KEEPER - AUTOMATED CHROMIUM REAL-TIME AUDIO+VIDEO RECORDER
 * This script runs the game naturally, triggers browser-side MediaRecorder inside Chromium,
 * grabs the pristine WebM track with integrated audio streams via a Node.js bridge,
 * and outputs a perfectly synchronized 4K high-compatibility MP4 video file.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function main() {
    console.log("-----------------------------------------------------------------");
    console.log("⚽ REAL-TIME BROWSER-SIDE AUDIO & VIDEO RECORDING SHURU HO RAHA HAI ⚽");
    console.log("-----------------------------------------------------------------");

    const webmPath = path.resolve(__dirname, 'recording_raw.webm');
    const mp4Path = path.resolve(__dirname, 'beat_the_keeper_4k.mp4');

    // Setup active state promises
    let resolveRecording;
    const recordingPromise = new Promise((resolve) => {
        resolveRecording = resolve;
    });

    // Chromium launch flags for headless audio loopback capture
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--autoplay-policy=no-user-gesture-required',
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--disable-web-security',
            '--allow-file-access-from-files'
        ]
    });

    const context = await browser.newContext({
        permissions: ['microphone'], // Allows loopback synthesizers audio stream capturing without system audio hardware
    });

    const page = await context.newPage();

    // Widescreen 4K Viewport mapping (3840 x 2160 pixels)
    await page.setViewportSize({ width: 3840, height: 2160 });

    // Expose Node.js Bridge function
    await page.exposeFunction('saveVideoChunkToDisk', (base64Data) => {
        console.log("⚡ Success! Browser-side MediaRecorder stream buffer fully received via Bridge!");
        const buffer = Buffer.from(base64Data, 'base64');
        fs.writeFileSync(webmPath, buffer);
        console.log(`💾 Raw WebM written successfully to path: ${webmPath}`);
        resolveRecording();
    });

    // Mapping game URL
    const fileUrl = `file://${path.resolve(__dirname, 'beat_the_keeper.html')}?headless=true`;
    console.log(`Loading Game URL: ${fileUrl}`);
    
    await page.goto(fileUrl);
    console.log("Waiting for game simulation, telemetry rounds, and real-time audio recording stream to end...");

    // Set maximum timeout of 12 minutes (720,000 ms) in case of any pipeline deadlock
    await Promise.race([
        recordingPromise,
        new Promise((_, reject) => setTimeout(() => reject(new Error("Recording timed out after 12 minutes.")), 720000))
    ]);

    await browser.close();

    console.log("-----------------------------------------------------------------");
    console.log("🔄 REMUXING WEBM TO COMPATIBLE MP4 USING FFMPEG 🔄");
    console.log("-----------------------------------------------------------------");

    try {
        console.log("Encoding audio tracks & packaging H.264 compatible MP4 video stream...");
        // Convert VP8/VP9 WebM track to standard H.264 + AAC with extreme high fidelity preset
        execSync(`ffmpeg -i "${webmPath}" -vcodec libx264 -pix_fmt yuv420p -preset fast -crf 17 -acodec aac -b:a 192k -y "${mp4Path}"`, { stdio: 'inherit' });
        console.log(`🎉 Perfect 4K MP4 with synced audio created successfully at: ${mp4Path}`);
        
        // Remove raw WebM temp file to keep workspace clean
        if (fs.existsSync(webmPath)) {
            fs.unlinkSync(webmPath);
        }
    } catch (err) {
        console.error("FFmpeg conversion failed. Attempting copy container container remux bypass...", err);
        try {
            execSync(`ffmpeg -i "${webmPath}" -c copy -y "${mp4Path}"`, { stdio: 'inherit' });
        } catch (copyErr) {
            console.error("Backup copy remux failed as well.", copyErr);
        }
    }
}

main().catch(err => {
    console.error("Critical automated pipeline execution failed:", err);
    process.exit(1);
});

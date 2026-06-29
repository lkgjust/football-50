/**
 * BEAT THE KEEPER - HEADLESS RENDERING PIPELINE
 * Playwright deterministic automation engine combined with lossy-less piping
 * and pristine FFmpeg Lanczos 4K (3840x2160) scaling blocks.
 */

const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

async function main() {
    console.log("-----------------------------------------------------------------");
    console.log("⚽ BEAT THE KEEPER - 4K ULTRA HD AUTOMATED RENDERER SHURU HO RAHA HAI ⚽");
    console.log("-----------------------------------------------------------------");

    // Headless Browser Launch karein
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--disable-web-security',
            '--allow-file-access-from-files',
            '--force-device-scale-factor=1',
            '--disable-gpu-vsync'
        ]
    });

    const page = await browser.newPage();
    
    // Viewport precisely set as 1080p standard layout box
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Local workspace index file mapping
    const fileUrl = `file://${path.resolve(__dirname, 'beat_the_keeper.html')}?headless=true`;
    console.log(`Loading Game URL: ${fileUrl}`);
    await page.goto(fileUrl);

    // Initial stabilization load window setup
    await page.waitForTimeout(2000);

    // Canvas scaling to standard 1080p (0.5x coordinate multiplier)
    await page.evaluate(() => {
        window.setRenderScale(0.5);
    });

    // Output video container path definition
    const outputVideoPath = path.resolve(__dirname, 'beat_the_keeper_4k_lanczos.mp4');

    /**
     * FFmpeg pipeline command mapping:
     * - Takes PNG stream from stdin pipe (-f image2pipe -vcodec png)
     * - Reads at 30 fps locked target (-r 30)
     * - Upscales from 1080p to 4K using advanced 'lanczos' algorithm
     * - Codes to highly-compatible H.264 mp4 codec
     */
    const ffmpegArgs = [
        '-f', 'image2pipe',
        '-vcodec', 'png',
        '-r', '30',
        '-i', '-',
        '-vf', 'scale=3840:2160:flags=lanczos',
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-crf', '16',                  // Extreme high-bitrate visual sharpness quality definition
        '-preset', 'fast',
        '-y',
        outputVideoPath
    ];

    console.log(`FFmpeg upscale pipeline target initialized! Saving to: ${outputVideoPath}`);
    const ffmpeg = spawn('ffmpeg', ffmpegArgs);

    ffmpeg.stderr.on('data', (data) => {
        // Log basic encoding telemetry logs safely
        const logStr = data.toString();
        if (logStr.includes('frame=') || logStr.includes('fps=')) {
            process.stdout.write(`\rFFmpeg Telemetry: ${logStr.trim().split('\n').pop()}`);
        }
    });

    ffmpeg.on('close', (code) => {
        console.log(`\nFFmpeg Process completed with termination code: ${code}`);
    });

    let frameCount = 0;
    let keepRunning = true;
    const canvasSelector = '#physics-canvas';

    console.log("Deterministic stepping framework capturing initialized...");

    while (keepRunning) {
        // Execute 1 frame increments strictly inside headless Matter.js sandbox context
        const status = await page.evaluate(() => {
            return window.stepFrame();
        });

        // Capture standard lossless canvas frame PNG buffer
        const canvasElement = await page.locator(canvasSelector);
        const imageBuffer = await canvasElement.screenshot({ type: 'png' });

        // Pipe directly to FFmpeg process input to bypass disk I/O lag entirely
        ffmpeg.stdin.write(imageBuffer);

        frameCount++;

        if (frameCount % 60 === 0) {
            console.log(`\n[RENDER STATE] Frame count: ${frameCount} | Current Round: ${status.currentRound} | Active marbles: ${status.totalMarbles}`);
        }

        // Termination target constraint: Champion is decided!
        if (status.isGameOver) {
            console.log(`\n👑 Grand Champion decided successfully at frame: ${frameCount}! Ending capture loop.`);
            keepRunning = false;
        }

        // Safety limit: 12,000 frames (~6 mins max run time) to prevent cloud billing loops
        if (frameCount > 12000) {
            console.log("\n[WARNING] Video threshold safely exceeded. Terminating task.");
            keepRunning = false;
        }
    }

    // Terminate streams
    ffmpeg.stdin.end();

    console.log("Saving complete upscaled video elements...");
    await browser.close();

    console.log("-----------------------------------------------------------------");
    console.log("🎉 RENDERING & CRISP 4K LANCZOS ENCODING FINISHED SUCCESSFULLY! 🎉");
    console.log("-----------------------------------------------------------------");
}

main().catch(err => {
    console.error("Critical rendering execution failed:", err);
});
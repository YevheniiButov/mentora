// ============================================
// 🔥 DOOM ENGINE - SECRET METAL DOOR! 🔥
// Добавь эту часть В САМЫЙ КОНЕЦ dentist_dash.html перед </script>
// ============================================

// ===== GAME MODE SYSTEM =====
let gameMode = 'platformer'; // 'platformer' or 'doom'
let doomDoor = null; // Metal door object

// ===== DOOM PLAYER (3D) =====
let player3D = {
    x: 1.5,           // Position in grid
    y: 1.5,
    dir: 0,           // Direction angle (radians)
    fov: Math.PI / 3, // Field of view
    health: 100,
    ammo: 100,
    moveSpeed: 0.08,
    rotSpeed: 0.05
};

// ===== DOOM MAP (Wolfenstein style grid) =====
let doomMap = [];
let doomEnemies = [];
let doomProjectiles = [];

// ===== TEXTURES/COLORS =====
const DOOM_COLORS = {
    wall: '#444',        // Metal
    wall2: '#666',       // Lighter metal
    ceil: '#111',        // Dark ceiling
    floor: '#333',       // Floor
    enemy: '#00fc00',    // Green bacteria
    door: '#8b4513',     // Brown door
    key: '#fcfc00'       // Yellow key
};

// ===== INITIALIZE DOOM MODE =====
function initDoomMode() {
    console.log('🔥 ENTERING DOOM MODE!');
    gameMode = 'doom';
    
    // Create simple DOOM map (10x10 grid, 1 = wall, 0 = empty)
    doomMap = [
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,1,1,0,0,1],
        [1,0,1,0,0,0,1,0,0,1],
        [1,0,1,1,2,0,1,0,0,1], // 2 = locked door
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,1,0,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,3,1], // 3 = exit door
        [1,1,1,1,1,1,1,1,1,1]
    ];
    
    // Spawn player in DOOM world
    player3D.x = 1.5;
    player3D.y = 1.5;
    player3D.dir = 0;
    player3D.health = 100;
    player3D.ammo = 100;
    
    // Spawn DOOM enemies (bacteria monsters!)
    doomEnemies = [
        { x: 3.5, y: 3.5, health: 30, alive: true, distance: 0 },
        { x: 6.5, y: 2.5, health: 30, alive: true, distance: 0 },
        { x: 7.5, y: 6.5, health: 30, alive: true, distance: 0 },
        { x: 4.5, y: 7.5, health: 30, alive: true, distance: 0 }
    ];
    
    doomProjectiles = [];
    
    playSound('warp'); // Sound effect
}

// ===== EXIT DOOM MODE =====
function exitDoomMode() {
    console.log('🚪 EXITING DOOM - BACK TO 2D!');
    gameMode = 'platformer';
    // Return player to 2D near the door
    player.x = doomDoor.x + 100;
    player.y = doomDoor.y;
    cameraX = Math.max(0, player.x - 400);
    playSound('warp');
}

// ===== ADD METAL DOOR TO 2D LEVEL =====
function addDoomDoorToLevel() {
    // Add secret metal door somewhere in the level
    doomDoor = {
        x: LEVEL_WIDTH - 1200, // Before boss
        y: 470,
        width: 50,
        height: 80,
        discovered: false
    };
    
    console.log('🚪 DOOM DOOR ADDED at x:', doomDoor.x);
}

// ===== MODIFY EXISTING initLevel() =====
// Add this at the END of your initLevel() function:
// addDoomDoorToLevel();

// ===== DOOM UPDATE LOGIC =====
function updateDoom() {
    // === MOVEMENT ===
    // W/Up - move forward
    if (keys['w'] || keys['W'] || keys['ArrowUp']) {
        const newX = player3D.x + Math.cos(player3D.dir) * player3D.moveSpeed;
        const newY = player3D.y + Math.sin(player3D.dir) * player3D.moveSpeed;
        
        // Check collision
        if (doomMap[Math.floor(newY)][Math.floor(newX)] === 0) {
            player3D.x = newX;
            player3D.y = newY;
        }
    }
    
    // S/Down - move backward
    if (keys['s'] || keys['S'] || keys['ArrowDown']) {
        const newX = player3D.x - Math.cos(player3D.dir) * player3D.moveSpeed;
        const newY = player3D.y - Math.sin(player3D.dir) * player3D.moveSpeed;
        
        if (doomMap[Math.floor(newY)][Math.floor(newX)] === 0) {
            player3D.x = newX;
            player3D.y = newY;
        }
    }
    
    // A/Left - rotate left
    if (keys['a'] || keys['A'] || keys['ArrowLeft']) {
        player3D.dir -= player3D.rotSpeed;
    }
    
    // D/Right - rotate right
    if (keys['d'] || keys['D'] || keys['ArrowRight']) {
        player3D.dir += player3D.rotSpeed;
    }
    
    // === SHOOTING ===
    if (keyCodes['KeyX'] && player3D.ammo > 0) {
        // Shoot projectile
        if (!window.doomShootCooldown || window.doomShootCooldown <= 0) {
            doomProjectiles.push({
                x: player3D.x,
                y: player3D.y,
                dir: player3D.dir,
                speed: 0.15,
                life: 60
            });
            player3D.ammo--;
            window.doomShootCooldown = 10;
            playSound('shoot');
        }
    }
    if (window.doomShootCooldown > 0) window.doomShootCooldown--;
    
    // === UPDATE PROJECTILES ===
    doomProjectiles = doomProjectiles.filter(p => {
        p.x += Math.cos(p.dir) * p.speed;
        p.y += Math.sin(p.dir) * p.speed;
        p.life--;
        
        // Check wall collision
        if (doomMap[Math.floor(p.y)][Math.floor(p.x)] !== 0) {
            return false; // Remove
        }
        
        // Check enemy collision
        let hit = false;
        doomEnemies.forEach(enemy => {
            if (enemy.alive) {
                const dist = Math.hypot(enemy.x - p.x, enemy.y - p.y);
                if (dist < 0.3) {
                    enemy.health -= 10;
                    if (enemy.health <= 0) {
                        enemy.alive = false;
                        score += 1000;
                        playSound('explosion');
                    } else {
                        playSound('hit');
                    }
                    hit = true;
                }
            }
        });
        
        return !hit && p.life > 0;
    });
    
    // === UPDATE ENEMIES ===
    doomEnemies.forEach(enemy => {
        if (!enemy.alive) return;
        
        // Calculate distance and angle to player
        const dx = player3D.x - enemy.x;
        const dy = player3D.y - enemy.y;
        enemy.distance = Math.hypot(dx, dy);
        
        // Simple AI: move towards player
        if (enemy.distance > 1.5) {
            const angle = Math.atan2(dy, dx);
            const newX = enemy.x + Math.cos(angle) * 0.02;
            const newY = enemy.y + Math.sin(angle) * 0.02;
            
            // Check collision
            if (doomMap[Math.floor(newY)][Math.floor(newX)] === 0) {
                enemy.x = newX;
                enemy.y = newY;
            }
        }
        
        // Attack player if close
        if (enemy.distance < 1.0) {
            player3D.health -= 1;
            if (player3D.health <= 0) {
                // Game over!
                lives--;
                if (lives <= 0) {
                    gameOver();
                } else {
                    // Reset DOOM level
                    initDoomMode();
                }
            }
        }
    });
    
    // === CHECK EXIT ===
    // If player reaches exit door (cell 3)
    const cellX = Math.floor(player3D.x);
    const cellY = Math.floor(player3D.y);
    if (doomMap[cellY][cellX] === 3) {
        // Exit DOOM mode!
        score += 5000; // Bonus for completing DOOM level!
        exitDoomMode();
    }
}

// ===== DOOM RENDERING (RAYCASTING) =====
function renderDoom() {
    const screenWidth = canvas.width;
    const screenHeight = canvas.height;
    
    // === RENDER CEILING & FLOOR ===
    ctx.fillStyle = DOOM_COLORS.ceil;
    ctx.fillRect(0, 0, screenWidth, screenHeight / 2);
    
    ctx.fillStyle = DOOM_COLORS.floor;
    ctx.fillRect(0, screenHeight / 2, screenWidth, screenHeight / 2);
    
    // === RAYCASTING ===
    const numRays = screenWidth / 2; // Cast 1 ray per 2 pixels for performance
    
    for (let i = 0; i < numRays; i++) {
        // Calculate ray angle
        const cameraX = 2 * i / numRays - 1; // x in camera space
        const rayAngle = player3D.dir + Math.atan(cameraX * Math.tan(player3D.fov / 2));
        
        // Ray direction
        const rayDirX = Math.cos(rayAngle);
        const rayDirY = Math.sin(rayAngle);
        
        // DDA algorithm (Digital Differential Analysis)
        let mapX = Math.floor(player3D.x);
        let mapY = Math.floor(player3D.y);
        
        // Length of ray from current position to next x or y-side
        const deltaDistX = Math.abs(1 / rayDirX);
        const deltaDistY = Math.abs(1 / rayDirY);
        
        // Calculate step and initial sideDist
        let stepX, stepY;
        let sideDistX, sideDistY;
        
        if (rayDirX < 0) {
            stepX = -1;
            sideDistX = (player3D.x - mapX) * deltaDistX;
        } else {
            stepX = 1;
            sideDistX = (mapX + 1.0 - player3D.x) * deltaDistX;
        }
        
        if (rayDirY < 0) {
            stepY = -1;
            sideDistY = (player3D.y - mapY) * deltaDistY;
        } else {
            stepY = 1;
            sideDistY = (mapY + 1.0 - player3D.y) * deltaDistY;
        }
        
        // Perform DDA
        let hit = 0;
        let side; // Was a NS or EW wall hit?
        
        while (hit === 0) {
            // Jump to next map square
            if (sideDistX < sideDistY) {
                sideDistX += deltaDistX;
                mapX += stepX;
                side = 0;
            } else {
                sideDistY += deltaDistY;
                mapY += stepY;
                side = 1;
            }
            
            // Check if ray has hit a wall
            if (mapY >= 0 && mapY < doomMap.length && 
                mapX >= 0 && mapX < doomMap[0].length) {
                hit = doomMap[mapY][mapX];
            } else {
                hit = 1; // Out of bounds = wall
            }
        }
        
        // Calculate distance
        let perpWallDist;
        if (side === 0) {
            perpWallDist = (mapX - player3D.x + (1 - stepX) / 2) / rayDirX;
        } else {
            perpWallDist = (mapY - player3D.y + (1 - stepY) / 2) / rayDirY;
        }
        
        // Calculate height of line to draw
        const lineHeight = Math.floor(screenHeight / perpWallDist);
        
        // Calculate lowest and highest pixel to fill
        const drawStart = Math.max(0, Math.floor(-lineHeight / 2 + screenHeight / 2));
        const drawEnd = Math.min(screenHeight, Math.floor(lineHeight / 2 + screenHeight / 2));
        
        // Choose wall color based on type
        let wallColor = DOOM_COLORS.wall;
        if (hit === 2) wallColor = DOOM_COLORS.door; // Door
        if (hit === 3) wallColor = '#00fc00'; // Exit (green!)
        
        // Shade based on side (like Wolfenstein!)
        if (side === 1) {
            wallColor = darkenColor(wallColor, 0.7);
        }
        
        // Draw wall slice
        ctx.fillStyle = wallColor;
        const x = i * 2;
        ctx.fillRect(x, drawStart, 2, drawEnd - drawStart);
    }
    
    // === RENDER SPRITES (ENEMIES) ===
    doomEnemies.forEach(enemy => {
        if (!enemy.alive) return;
        
        // Transform sprite position to relative to camera
        const spriteX = enemy.x - player3D.x;
        const spriteY = enemy.y - player3D.y;
        
        // Transform using camera matrix
        const invDet = 1.0 / (Math.cos(player3D.dir + Math.PI/2) * Math.sin(player3D.dir) - 
                               Math.sin(player3D.dir + Math.PI/2) * Math.cos(player3D.dir));
        
        const transformX = invDet * (Math.sin(player3D.dir) * spriteX - Math.cos(player3D.dir) * spriteY);
        const transformY = invDet * (-Math.sin(player3D.dir + Math.PI/2) * spriteX + 
                                     Math.cos(player3D.dir + Math.PI/2) * spriteY);
        
        if (transformY > 0) { // Sprite is in front
            const spriteScreenX = Math.floor((screenWidth / 2) * (1 + transformX / transformY));
            
            // Calculate sprite height
            const spriteHeight = Math.abs(Math.floor(screenHeight / transformY));
            const drawStartY = Math.max(0, -spriteHeight / 2 + screenHeight / 2);
            const drawEndY = Math.min(screenHeight, spriteHeight / 2 + screenHeight / 2);
            
            // Calculate sprite width
            const spriteWidth = Math.abs(Math.floor(screenHeight / transformY));
            const drawStartX = Math.max(0, -spriteWidth / 2 + spriteScreenX);
            const drawEndX = Math.min(screenWidth, spriteWidth / 2 + spriteScreenX);
            
            // Draw enemy sprite (green bacteria)
            ctx.fillStyle = DOOM_COLORS.enemy;
            ctx.fillRect(drawStartX, drawStartY, drawEndX - drawStartX, drawEndY - drawStartY);
            
            // Enemy eyes (red)
            ctx.fillStyle = '#fc0000';
            const eyeSize = Math.max(2, spriteWidth / 8);
            ctx.fillRect(drawStartX + spriteWidth * 0.3, drawStartY + spriteHeight * 0.3, eyeSize, eyeSize);
            ctx.fillRect(drawStartX + spriteWidth * 0.6, drawStartY + spriteHeight * 0.3, eyeSize, eyeSize);
        }
    });
    
    // === HUD ===
    ctx.save();
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    ctx.fillRect(0, screenHeight - 60, screenWidth, 60);
    
    ctx.fillStyle = '#fff';
    ctx.font = '16px "Press Start 2P"';
    ctx.fillText(`HP: ${Math.max(0, Math.floor(player3D.health))}`, 20, screenHeight - 30);
    ctx.fillText(`AMMO: ${player3D.ammo}`, 250, screenHeight - 30);
    ctx.fillText(`SCORE: ${score}`, 500, screenHeight - 30);
    
    // Crosshair
    ctx.fillStyle = '#fc0000';
    ctx.fillRect(screenWidth/2 - 10, screenHeight/2 - 2, 20, 4);
    ctx.fillRect(screenWidth/2 - 2, screenHeight/2 - 10, 4, 20);
    
    // Instructions
    ctx.fillStyle = '#fcfc00';
    ctx.font = '10px "Press Start 2P"';
    ctx.fillText('WASD/ARROWS: MOVE | X: SHOOT | REACH GREEN EXIT!', 50, 30);
    
    ctx.restore();
}

// Helper: Darken color
function darkenColor(color, factor) {
    const r = parseInt(color.slice(1,3), 16);
    const g = parseInt(color.slice(3,5), 16);
    const b = parseInt(color.slice(5,7), 16);
    
    return '#' + 
        Math.floor(r * factor).toString(16).padStart(2, '0') +
        Math.floor(g * factor).toString(16).padStart(2, '0') +
        Math.floor(b * factor).toString(16).padStart(2, '0');
}

// ===== MODIFY MAIN GAME LOOP =====
// Replace your existing update() with this:
/*
function update() {
    if (gameMode === 'doom') {
        updateDoom();
        return;
    }
    
    // ... rest of your existing update() code ...
}
*/

// ===== MODIFY MAIN RENDER =====
// Replace your existing render() with this:
/*
function render() {
    if (gameMode === 'doom') {
        renderDoom();
        return;
    }
    
    // ... rest of your existing render() code ...
}
*/

// ===== RENDER DOOM DOOR IN 2D =====
function renderDoomDoor() {
    if (!doomDoor || inUnderground) return;
    
    // Metal door
    ctx.fillStyle = '#444';
    ctx.fillRect(doomDoor.x, doomDoor.y, doomDoor.width, doomDoor.height);
    
    // Rivets
    ctx.fillStyle = '#666';
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 5; j++) {
            ctx.fillRect(
                doomDoor.x + 10 + i * 15,
                doomDoor.y + 10 + j * 15,
                4, 4
            );
        }
    }
    
    // Mysterious glow
    const time = Date.now() / 200;
    const glow = 0.3 + Math.sin(time) * 0.3;
    ctx.fillStyle = '#fc0000';
    ctx.globalAlpha = glow;
    ctx.fillRect(doomDoor.x + doomDoor.width/2 - 8, doomDoor.y + doomDoor.height/2 - 8, 16, 16);
    ctx.globalAlpha = 1;
    
    // Skull symbol
    ctx.fillStyle = '#fcfc00';
    ctx.fillRect(doomDoor.x + doomDoor.width/2 - 6, doomDoor.y + doomDoor.height/2 - 6, 12, 8);
    ctx.fillStyle = '#fc0000';
    ctx.fillRect(doomDoor.x + doomDoor.width/2 - 4, doomDoor.y + doomDoor.height/2 - 4, 3, 3);
    ctx.fillRect(doomDoor.x + doomDoor.width/2 + 1, doomDoor.y + doomDoor.height/2 - 4, 3, 3);
    
    // Hint text if player is near
    if (checkCollision(player, doomDoor)) {
        ctx.fillStyle = '#fff';
        ctx.font = '10px "Press Start 2P"';
        ctx.fillText('↓ ENTER DOOM', doomDoor.x - 20, doomDoor.y - 15);
        
        // Check for enter key
        if (keys['ArrowDown']) {
            initDoomMode();
        }
    }
}

// ===== ADD THIS TO YOUR EXISTING render() FUNCTION =====
// After rendering pipes, add:
// renderDoomDoor();

console.log('🔥 DOOM ENGINE LOADED! Add to your code:');
console.log('1. Call addDoomDoorToLevel() at end of initLevel()');
console.log('2. Call renderDoomDoor() in render() after pipes');
console.log('3. Wrap update() and render() with gameMode checks');

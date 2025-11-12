let currentPlanId = null;
let map = null;
let recognition = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadMyPlans();
    initVoiceRecognition();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('generateBtn').addEventListener('click', generatePlan);
    document.getElementById('voiceBtn').addEventListener('click', toggleVoiceRecognition);
    document.getElementById('newPlanBtn').addEventListener('click', showInputSection);
    document.getElementById('backBtn').addEventListener('click', showInputSection);
    document.getElementById('expenseForm').addEventListener('submit', addExpense);
}

// 加载我的计划列表
async function loadMyPlans() {
    try {
        const response = await fetch('/api/my-plans');
        const data = await response.json();
        
        if (data.success) {
            const plansList = document.getElementById('plansList');
            plansList.innerHTML = '';
            
            data.plans.forEach(plan => {
                const planItem = document.createElement('div');
                planItem.className = 'plan-item';
                planItem.innerHTML = `
                    <div class="plan-item-content" onclick="loadPlan(${plan.id})">
                        <h4>${plan.title}</h4>
                        <small>${new Date(plan.created_at).toLocaleDateString()}</small>
                    </div>
                    <button class="btn-delete" onclick="deletePlan(event, ${plan.id})" title="删除计划">🗑️</button>
                `;
                plansList.appendChild(planItem);
            });
        }
    } catch (error) {
        console.error('加载计划失败:', error);
    }
}

// 生成旅行计划
async function generatePlan() {
    const userInput = document.getElementById('userInput').value;
    if (!userInput.trim()) {
        alert('请输入您的旅行需求');
        return;
    }

    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    generateBtn.textContent = '生成中...';

    try {
        const response = await fetch('/api/generate-plan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({input: userInput})
        });

        const data = await response.json();
        
        if (data.success) {
            currentPlanId = data.plan_id;
            displayPlan(data.plan);
            loadMyPlans();
        } else {
            alert('生成计划失败，请重试');
        }
    } catch (error) {
        console.error('生成计划错误:', error);
        alert('生成计划失败，请检查网络连接');
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = '生成计划';
    }
}

// 加载特定计划
async function loadPlan(planId) {
    try {
        const response = await fetch(`/api/plan/${planId}`);
        const data = await response.json();
        
        if (data.success) {
            currentPlanId = planId;
            displayPlan(data.plan.plan_data);
        }
    } catch (error) {
        console.error('加载计划失败:', error);
    }
}

// 显示计划
function displayPlan(plan) {
    document.getElementById('inputSection').style.display = 'none';
    document.getElementById('planSection').style.display = 'block';
    
    document.getElementById('planTitle').textContent = plan.destination || '旅行计划';
    
    // 显示预算摘要
    if (plan.budget_breakdown) {
        const budgetHtml = `
            <h3>预算概览</h3>
            <p><strong>总预算：</strong>¥${plan.budget_breakdown.total || 0}</p>
            <ul>
                <li>交通：¥${plan.budget_breakdown.transportation || 0}</li>
                <li>住宿：¥${plan.budget_breakdown.accommodation || 0}</li>
                <li>餐饮：¥${plan.budget_breakdown.food || 0}</li>
                <li>活动：¥${plan.budget_breakdown.activities || 0}</li>
                <li>购物：¥${plan.budget_breakdown.shopping || 0}</li>
                <li>应急：¥${plan.budget_breakdown.emergency || 0}</li>
            </ul>
        `;
        document.getElementById('budgetSummary').innerHTML = budgetHtml;
    }
    
    // 显示行程
    if (plan.itinerary) {
        let itineraryHtml = '<h3>行程安排</h3>';
        plan.itinerary.forEach(day => {
            itineraryHtml += `
                <div class="day-item">
                    <h4>第 ${day.day} 天 ${day.date || ''}</h4>
                    <ul>
                        ${day.activities.map(act => `
                            <li>
                                <strong>${act.time}</strong> - ${act.activity}
                                <br><small>📍 ${act.location} | ¥${act.cost || 0}</small>
                                ${act.notes ? `<br><small>${act.notes}</small>` : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        });
        document.getElementById('itinerary').innerHTML = itineraryHtml;
    }
    
    // 显示住宿
    if (plan.accommodation) {
        let accommodationHtml = '<h3>住宿安排</h3><ul>';
        plan.accommodation.forEach(hotel => {
            accommodationHtml += `
                <li>
                    <strong>${hotel.name}</strong> - ${hotel.location}
                    <br><small>${hotel.nights} 晚 | ¥${hotel.cost}</small>
                </li>
            `;
        });
        accommodationHtml += '</ul>';
        document.getElementById('accommodation').innerHTML = accommodationHtml;
    }
    
    // 显示建议
    if (plan.tips) {
        let tipsHtml = '<h3>旅行建议</h3><ul>';
        plan.tips.forEach(tip => {
            tipsHtml += `<li>${tip}</li>`;
        });
        tipsHtml += '</ul>';
        document.getElementById('tips').innerHTML = tipsHtml;
    }
    
    // 初始化地图并显示行程路线
    initMapWithItinerary(plan);
}

// 初始化地图并显示行程路线
function initMapWithItinerary(plan) {
    if (!window.AMap) {
        console.warn('高德地图未加载');
        document.getElementById('map').innerHTML = '<p style="text-align:center;padding:50px;">地图加载失败，请检查网络连接</p>';
        return;
    }
    
    if (map) {
        map.destroy();
    }
    
    // 创建地图实例
    map = new AMap.Map('map', {
        zoom: 12,
        center: [116.397428, 39.90923],
        viewMode: '2D',
        mapStyle: 'amap://styles/normal'
    });
    
    // 收集所有景点位置
    const locations = [];
    const destination = plan.destination || '北京';
    
    // 如果有行程安排，提取所有景点
    if (plan.itinerary && plan.itinerary.length > 0) {
        plan.itinerary.forEach(day => {
            if (day.activities && day.activities.length > 0) {
                day.activities.forEach(activity => {
                    if (activity.location) {
                        locations.push({
                            name: activity.activity,
                            location: activity.location,
                            time: activity.time,
                            day: day.day,
                            cost: activity.cost,
                            notes: activity.notes
                        });
                    }
                });
            }
        });
    }
    
    // 如果有住宿信息，也添加到地图
    if (plan.accommodation && plan.accommodation.length > 0) {
        plan.accommodation.forEach(hotel => {
            if (hotel.location) {
                locations.push({
                    name: hotel.name,
                    location: hotel.location,
                    type: 'hotel',
                    cost: hotel.cost,
                    nights: hotel.nights
                });
            }
        });
    }
    
    console.log('提取的位置信息:', locations);
    
    // 如果有具体景点，逐个标记
    if (locations.length > 0) {
        geocodeAndMarkLocations(locations, destination);
    } else {
        // 如果没有具体景点，只标记目的地
        geocodeDestination(destination);
    }
}

// 地理编码并标记所有位置
function geocodeAndMarkLocations(locations, cityName) {
    const geocoder = new AMap.Geocoder({
        city: cityName
    });
    
    const markers = [];
    const bounds = [];
    let completedCount = 0;
    
    locations.forEach((loc, index) => {
        // 尝试地理编码
        geocoder.getLocation(loc.location, function(status, result) {
            completedCount++;
            
            if (status === 'complete' && result.info === 'OK' && result.geocodes.length > 0) {
                const position = result.geocodes[0].location;
                bounds.push([position.lng, position.lat]);
                
                // 根据类型选择图标颜色
                let iconColor = loc.type === 'hotel' ? '#FF6B6B' : '#4ECDC4';
                let label = loc.type === 'hotel' ? '🏨' : `${index + 1}`;
                
                // 创建标记
                const marker = new AMap.Marker({
                    position: [position.lng, position.lat],
                    title: loc.name,
                    label: {
                        content: `<div style="background:${iconColor};color:white;padding:4px 8px;border-radius:12px;font-weight:bold;">${label}</div>`,
                        offset: new AMap.Pixel(0, -30)
                    },
                    map: map
                });
                
                // 创建信息窗体
                let content = `
                    <div style="padding:12px;min-width:200px;">
                        <h4 style="margin:0 0 8px 0;color:#333;">${loc.name}</h4>
                        <p style="margin:4px 0;color:#666;"><strong>📍 位置：</strong>${loc.location}</p>
                `;
                
                if (loc.day) {
                    content += `<p style="margin:4px 0;color:#666;"><strong>📅 第 ${loc.day} 天</strong></p>`;
                }
                if (loc.time) {
                    content += `<p style="margin:4px 0;color:#666;"><strong>🕐 时间：</strong>${loc.time}</p>`;
                }
                if (loc.cost) {
                    content += `<p style="margin:4px 0;color:#666;"><strong>💰 费用：</strong>¥${loc.cost}</p>`;
                }
                if (loc.nights) {
                    content += `<p style="margin:4px 0;color:#666;"><strong>🌙 住宿：</strong>${loc.nights} 晚</p>`;
                }
                if (loc.notes) {
                    content += `<p style="margin:4px 0;color:#999;font-size:12px;">${loc.notes}</p>`;
                }
                
                content += '</div>';
                
                const infoWindow = new AMap.InfoWindow({
                    content: content,
                    offset: new AMap.Pixel(0, -30)
                });
                
                marker.on('click', function() {
                    infoWindow.open(map, marker.getPosition());
                });
                
                markers.push(marker);
            } else {
                console.warn(`地理编码失败: ${loc.location}`, status, result);
            }
            
            // 所有位置处理完成后，调整地图视野
            if (completedCount === locations.length) {
                if (bounds.length > 0) {
                    map.setFitView(markers, false, [50, 50, 50, 50]);
                    
                    // 如果有多个点，绘制路线
                    if (bounds.length > 1) {
                        drawRoute(bounds);
                    }
                } else {
                    // 如果所有编码都失败，尝试搜索目的地
                    geocodeDestination(cityName);
                }
            }
        });
    });
}

// 绘制路线
function drawRoute(points) {
    if (points.length < 2) return;
    
    // 创建折线
    const polyline = new AMap.Polyline({
        path: points,
        strokeColor: '#4ECDC4',
        strokeWeight: 4,
        strokeOpacity: 0.8,
        strokeStyle: 'solid',
        lineJoin: 'round',
        lineCap: 'round',
        zIndex: 50,
        showDir: true
    });
    
    map.add(polyline);
}

// 地理编码目的地（备用方案）
function geocodeDestination(destination) {
    const geocoder = new AMap.Geocoder({
        city: '全国'
    });
    
    geocoder.getLocation(destination, function(status, result) {
        if (status === 'complete' && result.info === 'OK') {
            const location = result.geocodes[0].location;
            
            map.setCenter([location.lng, location.lat]);
            map.setZoom(12);
            
            const marker = new AMap.Marker({
                position: [location.lng, location.lat],
                title: destination,
                map: map
            });
            
            const infoWindow = new AMap.InfoWindow({
                content: `<div style="padding:10px;"><strong>${destination}</strong></div>`
            });
            
            marker.on('click', function() {
                infoWindow.open(map, marker.getPosition());
            });
        } else {
            console.warn('目的地地理编码失败:', status, result);
            searchLocation(destination);
        }
    });
}

// 搜索位置（备用方案）
function searchLocation(keyword) {
    AMap.plugin('AMap.PlaceSearch', function() {
        const placeSearch = new AMap.PlaceSearch({
            city: '全国'
        });
        
        placeSearch.search(keyword, function(status, result) {
            if (status === 'complete' && result.poiList.pois.length > 0) {
                const poi = result.poiList.pois[0];
                const location = poi.location;
                
                map.setCenter([location.lng, location.lat]);
                map.setZoom(13);
                
                new AMap.Marker({
                    position: [location.lng, location.lat],
                    title: poi.name,
                    map: map
                });
            }
        });
    });
}

// 显示输入界面
function showInputSection() {
    document.getElementById('planSection').style.display = 'none';
    document.getElementById('inputSection').style.display = 'block';
    document.getElementById('userInput').value = '';
}

// 添加费用记录
async function addExpense(e) {
    e.preventDefault();
    
    if (!currentPlanId) {
        alert('请先选择一个计划');
        return;
    }
    
    const expenseData = {
        plan_id: currentPlanId,
        expense: {
            category: document.getElementById('expenseCategory').value,
            amount: parseFloat(document.getElementById('expenseAmount').value),
            description: document.getElementById('expenseDesc').value,
            date: document.getElementById('expenseDate').value
        }
    };
    
    try {
        const response = await fetch('/api/expense', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(expenseData)
        });
        
        const data = await response.json();
        if (data.success) {
            alert('费用记录已添加');
            document.getElementById('expenseForm').reset();
        }
    } catch (error) {
        console.error('添加费用失败:', error);
    }
}

// 初始化语音识别
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('userInput').value = transcript;
            document.getElementById('voiceBtn').textContent = '🎤 语音输入';
        };
        
        recognition.onerror = (event) => {
            console.error('语音识别错误:', event.error);
            document.getElementById('voiceBtn').textContent = '🎤 语音输入';
        };
        
        recognition.onend = () => {
            document.getElementById('voiceBtn').textContent = '🎤 语音输入';
        };
    } else {
        console.warn('浏览器不支持语音识别');
        document.getElementById('voiceBtn').disabled = true;
    }
}

// 切换语音识别
function toggleVoiceRecognition() {
    if (!recognition) {
        alert('您的浏览器不支持语音识别功能');
        return;
    }
    
    if (document.getElementById('voiceBtn').textContent.includes('停止')) {
        recognition.stop();
        document.getElementById('voiceBtn').textContent = '🎤 语音输入';
    } else {
        recognition.start();
        document.getElementById('voiceBtn').textContent = '🔴 停止录音';
    }
}

// 删除旅行计划
async function deletePlan(event, planId) {
    event.stopPropagation(); // 阻止事件冒泡，避免触发加载计划
    
    if (!confirm('确定要删除这个旅行计划吗？此操作无法撤销。')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/plan/${planId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('计划已删除');
            
            // 如果删除的是当前显示的计划，返回输入界面
            if (currentPlanId === planId) {
                showInputSection();
                currentPlanId = null;
            }
            
            // 重新加载计划列表
            loadMyPlans();
        } else {
            alert(data.message || '删除失败，请重试');
        }
    } catch (error) {
        console.error('删除计划错误:', error);
        alert('删除失败，请检查网络连接');
    }
}

/*
 Navicat Premium Dump Script

 Source Server         : local_mongo
 Source Server Type    : MongoDB
 Source Server Version : 80203 (8.2.3)
 Source Host           : localhost:27017
 Source Schema         : test

 Target Server Type    : MongoDB
 Target Server Version : 80203 (8.2.3)
 File Encoding         : 65001

 Date: 28/02/2026 11:43:11
*/


// ----------------------------
// Collection structure for agent_context_memory
// ----------------------------
db.getCollection("agent_context_memory").drop();
db.createCollection("agent_context_memory");
db.getCollection("agent_context_memory").createIndex({
    session_id: Int32("1"),
    agent_name: Int32("1")
}, {
    name: "session_id_1_agent_name_1"
});

// ----------------------------
// Documents of agent_context_memory
// ----------------------------

// ----------------------------
// Collection structure for dialog_messages
// ----------------------------
db.getCollection("dialog_messages").drop();
db.createCollection("dialog_messages");

// ----------------------------
// Documents of dialog_messages
// ----------------------------
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a10ff6e829f88a7ce9e8f8"),
    message_id: "msg_gIK8x-Jkp2BRyH-0",
    session_id: "session_JrRZOmBH57REbGtwfegBGA",
    role: "user",
    content: "故宫有什么好玩的？",
    metadata: { },
    created_at: ISODate("2026-02-27T03:31:02.929Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a11066e829f88a7ce9e8fa"),
    message_id: "msg_kkfh_sVUY4F_ULq1",
    session_id: "session_JrRZOmBH57REbGtwfegBGA",
    role: "assistant",
    content: "故宫（全称：北京故宫博物院），又称“紫禁城”，是世界上现存规模最大、保存最完整、历史最悠久的古代木结构宫殿建筑群，也是中国明清两代24位皇帝的皇家宫殿，距今已有600多年历史（始建于明永乐四年，1406年）。它不仅是一座建筑奇迹，更是一座浓缩中华文明的“立体百科全书”。下面为你详细梳理——**故宫到底有什么好玩的？**（兼顾文化深度、游览趣味与实用体验👇）\n\n---\n\n🎯 **一、必看精华：不可错过的“镇宫之宝”与核心打卡点**\n\n1. **中轴线经典路线（适合首次游览｜约2.5–3小时）**  \n   这是故宫的“龙脉”，体现古代皇权至高无上的礼制思想：\n   - 🚪 **午门**：故宫正门，外形如展翅凤凰，俗称“推出午门斩首”其实是误传（明代实际多在此颁诏、献俘或举行廷杖）。登上午门城楼可俯瞰太和门广场，视野震撼。\n   - 🌟 **太和殿（金銮殿）**：故宫最高大、最尊贵的建筑，皇帝登基、大婚、命将出征等重大典礼在此举行。注意看屋顶11只脊兽（全国唯一），屋檐下金箔彩画、蟠龙金柱、髹金漆云龙纹宝座——细节处处彰显“九五之尊”。\n   - 🏯 **中和殿 & 保和殿**：中和殿是皇帝去太和殿前休息、阅册的地方；保和殿则是殿试场所（清代状元即诞生于此），乾隆后期还曾用作除夕赐宴外藩之地。\n   - 🧭 **乾清宫 & 坤宁宫 & 交泰殿（后三宫）**：象征“天地交泰，阴阳和谐”。乾清宫是明代及清初皇帝寝宫与理政处（康熙曾在此设南书房）；坤宁宫在清代改为萨满祭祀场所，并为帝后大婚洞房（如光绪大婚）；交泰殿内藏有25方“皇帝之宝”玉玺（代表皇权合法性）。\n   - 🌙 **御花园**：皇家私家园林典范！虽仅1.2公顷，却精巧绝伦：古柏参天、钦安殿香火绵延、千秋亭与万春亭双环抱式设计、太湖石堆叠的“堆秀山”可登顶远眺……还有连理柏、绛雪轩等充满故事的角落。\n\n2. **隐藏彩蛋·冷知识打卡点**\n   - 🔍 **断虹桥石狮群**（武英殿北侧）：18只神态各异的汉白玉石狮，其中一只“捂裆狮”憨态可掬，是游客最爱合影点；\n   - 🐉 **铜龟/铜鹤**（太和殿前）：象征长寿与祥瑞，但细看铜鹤尾部有被火烧过的痕迹——那是1900年八国联军侵华时留下的弹痕；\n   - 📜 **文华殿书画馆 / 武英殿陶瓷馆**（轮流开放）：常设展+特展轮换，如《石渠宝笈》展、苏轼主题展、历代陶瓷精粹展…真正“国宝级”真迹近距离观赏！\n\n---\n\n🎨 **二、深度体验：不止走马观花，还能这样玩！**\n\n✅ **【沉浸式文化体验】**  \n- 🎭 **宫廷戏剧演出**（慈宁宫区域，旺季周末）：由专业演员还原清代节庆礼仪、昆曲片段或“冰嬉”表演（冬季特色）；  \n- 📜 **“数字文物库” & “全景故宫”小程序**：提前线上360°云游+高清放大看文物细节（连《千里江山图》笔触都清晰可见）；  \n- 🧩 **故宫文创互动**：箭亭广场旁的“故宫教育中心”常设拓印、团扇绘制、榫卯拼装等亲子手工课（需提前预约）；\n\n✅ **【小众秘径推荐】**（避开人潮，感受静谧故宫）  \n- 🌿 **东六宫片区**（延禧宫、景阳宫、永和宫）：曾是后妃居所，现多设专题展（如清代后妃生活展、珍宝馆分馆）；延禧宫“水晶宫”遗址（未完工的西洋风格水殿）超有穿越感；  \n- 🌳 **慈宁宫花园**：专为太后太妃修建，比御花园更幽深，古树参天、苔痕斑驳，偶遇松鼠跳跃，是发呆放空首选；  \n- 📸 **西华门内筒子河畔**：傍晚时分，红墙碧水、垂柳拂面，倒影如画，摄影党私藏机位！\n\n✅ **【舌尖上的故宫】**  \n- 🥟 **角楼咖啡**：网红打卡地！窗边座位直面角楼+护城河，推荐“千里江山图”拉花咖啡、“朕的心意”点心礼盒；  \n- 🍵 **冰窖餐厅**（原清代皇家藏冰地窖改造）：冬日暖炉烤肉、夏日冰碗甜品，环境古韵十足；  \n- 🍜 **故宫火锅（已暂停营业，但未来可能回归）**：曾以“慈宁宫”“漱芳斋”命名锅底，配宫廷点心，仪式感满分！\n\n---\n\n📌 **三、实用Tips｜让你玩得更顺、更懂、更值！**\n\n🔹 **预约！预约！预约！**  \n→ 全网实名制预约（微信公众号“故宫博物院”或官网），旺季务必提前7天抢票（尤其节假日）；  \n→ 每日限流8万人，现场不售票；学生、老人、儿童免费（需预约）；\n\n🔹 **最佳游览时间**  \n⏰ 建议开馆即入（8:30）或下午2点后（人流减少，光线柔和适合拍照）；  \n☀️ 春秋最佳（4–5月海棠盛放，9–10月银杏金黄）；夏季备伞防晒，冬季穿厚袜+防滑鞋（金砖地砖易滑）；\n\n🔹 **省力动线建议**  \n✔️ 午门进 → 中轴线主殿 → 东六宫/西六宫选其一 → 御花园/慈宁宫花园 → 神武门出；  \n✔️ 想看文物重点：直奔文华殿（书画）、武英殿（陶瓷）、珍宝馆（养性殿+乐寿堂）、钟表馆（奉先殿）——⚠️这两馆需另购门票（10元/人，含在大门票内可选）；\n\n🔹 **贴心小物**  \n🎒 轻装上阵（安检严格，大包需寄存）；  \n👟 穿舒适平底鞋（日均2万步起步）；  \n📱 下载「故宫博物院」官方App（带AR导览、语音讲解、地图导航）；  \n📜 租电子讲解器（20元）或听免费AI语音导览（公众号内即可开启）；\n\n---\n\n✨ **最后送你一句故宫魂：**  \n> “它不是冰冷的红墙黄瓦，而是一本摊开的史书——  \n> 每一块金砖记得工匠的掌纹，每一道彩画藏着匠人的祈愿，  \n> 每一扇朱门后，都有过悲欢、权谋、诗酒与烟火。”  \n\n来故宫，不只是“到此一游”，而是推开一扇门，走进一段活着的历史。\n\n需要我帮你：  \n🔸 定制一日/半日游览路线（含交通+时间+避坑）？  \n🔸 推荐适合孩子/老人/摄影党的特别玩法？  \n🔸 解析某件文物背后的故事（比如《千里江山图》《金瓯永固杯》）？  \n🔸 或对比“故宫 vs 台北故宫 vs 沈阳故宫”的差异？  \n\n欢迎随时告诉我～ 😊  \n祝你在紫禁城里，遇见六百年的风雅与心跳 🌟",
    metadata: {
        intent: "info_query"
    },
    created_at: ISODate("2026-02-27T03:32:54.459Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a13258e829f88a7ce9e8fc"),
    message_id: "msg_gNCbwCrBjreQNTUy",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "user",
    content: "你好啊",
    metadata: { },
    created_at: ISODate("2026-02-27T05:57:44.476Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a1325de829f88a7ce9e8fe"),
    message_id: "msg_GEdwA_N7A8TAJceG",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "assistant",
    content: "你好啊！😊  \n很高兴见到你～  \n（悄悄说：刚刚还在故宫的红墙下“云逛”了一圈，正捧着一杯角楼咖啡看夕阳呢 ☕️🌅）\n\n有什么想聊的、想问的，或者需要帮忙的？  \n比如——  \n✅ 想规划一场说走就走的旅行？  \n✅ 对某个景点、历史故事、文化冷知识超好奇？  \n✅ 需要实用攻略、避坑提醒、小众玩法？  \n✅ 甚至只是想轻松聊聊天、听个有趣的小故事？  \n\n我随时在线，陪你一起发现世界的美与温度 🌍✨  \n来吧，你想从哪里开始？ 😄",
    metadata: {
        intent: "general_chat"
    },
    created_at: ISODate("2026-02-27T05:57:49.455Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a1326de829f88a7ce9e8ff"),
    message_id: "msg_XmGE12w1TIvn4Agz",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "user",
    content: "想去南京万",
    metadata: { },
    created_at: ISODate("2026-02-27T05:58:05.287Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a1326de829f88a7ce9e901"),
    message_id: "msg_ACnEm6pQKA7vooke",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "assistant",
    content: "好的，我来帮您规划旅行！请告诉我：\n1. 目的地城市\n2. 出发日期\n3. 旅行天数\n4. 您的偏好（如历史文化、自然风光等）",
    metadata: {
        intent: "trip_planning"
    },
    created_at: ISODate("2026-02-27T05:58:05.919Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a13287e829f88a7ce9e902"),
    message_id: "msg_rObqtbg61Xo5vmlp",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "user",
    content: "南京，2月28日，旅行一天，自然风光和历史文化",
    metadata: { },
    created_at: ISODate("2026-02-27T05:58:31.063Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a13288e829f88a7ce9e904"),
    message_id: "msg_qSNnlKw1xC1VqYAn",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "assistant",
    content: "好的，我来帮您规划旅行！请告诉我：\n1. 目的地城市\n2. 出发日期\n3. 旅行天数\n4. 您的偏好（如历史文化、自然风光等）",
    metadata: {
        intent: "trip_planning"
    },
    created_at: ISODate("2026-02-27T05:58:32.073Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a1328ce829f88a7ce9e905"),
    message_id: "msg_yqzT1Bjm554XC6aO",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "user",
    content: "上海2日游",
    metadata: { },
    created_at: ISODate("2026-02-27T05:58:36.351Z")
} ]);
db.getCollection("dialog_messages").insert([ {
    _id: ObjectId("69a1328ce829f88a7ce9e907"),
    message_id: "msg_M5YGDyQsomeZYmNK",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    role: "assistant",
    content: "好的，我来帮您规划旅行！请告诉我：\n1. 目的地城市\n2. 出发日期\n3. 旅行天数\n4. 您的偏好（如历史文化、自然风光等）",
    metadata: {
        intent: "trip_planning"
    },
    created_at: ISODate("2026-02-27T05:58:36.785Z")
} ]);

// ----------------------------
// Collection structure for dialog_sessions
// ----------------------------
db.getCollection("dialog_sessions").drop();
db.createCollection("dialog_sessions");
db.getCollection("dialog_sessions").createIndex({
    user_id: Int32("1"),
    last_message_at: Int32("-1")
}, {
    name: "user_id_1_last_message_at_-1"
});
db.getCollection("dialog_sessions").createIndex({
    session_id: Int32("1")
}, {
    name: "session_id_1",
    unique: true
});
db.getCollection("dialog_sessions").createIndex({
    status: Int32("1"),
    updated_at: Int32("-1")
}, {
    name: "status_1_updated_at_-1"
});

// ----------------------------
// Documents of dialog_sessions
// ----------------------------
db.getCollection("dialog_sessions").insert([ {
    _id: ObjectId("69a10ff1e829f88a7ce9e8f7"),
    session_id: "session_JrRZOmBH57REbGtwfegBGA",
    user_id: Int32("6"),
    context: { },
    message_count: Int32("2"),
    created_at: ISODate("2026-02-27T03:30:57.799Z"),
    updated_at: ISODate("2026-02-27T06:54:57.443Z"),
    is_active: true,
    title: "想去北京"
} ]);
db.getCollection("dialog_sessions").insert([ {
    _id: ObjectId("69a13251e829f88a7ce9e8fb"),
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    user_id: Int32("6"),
    context: { },
    message_count: Int32("8"),
    created_at: ISODate("2026-02-27T05:57:37.636Z"),
    updated_at: ISODate("2026-02-27T06:54:50.279Z"),
    is_active: true,
    title: "想去故宫"
} ]);

// ----------------------------
// Collection structure for douyin_hotboard
// ----------------------------
db.getCollection("douyin_hotboard").drop();
db.createCollection("douyin_hotboard");

// ----------------------------
// Documents of douyin_hotboard
// ----------------------------
db.getCollection("douyin_hotboard").insert([ {
    _id: "20260226",
    type: "douyin",
    update_time: "2026-02-26T02:07:50.646Z",
    list: [
        {
            index: Int32("1"),
            title: "报告揭美收割全球虚拟货币资产",
            url: "https://www.douyin.com/search/%E6%8A%A5%E5%91%8A%E6%8F%AD%E7%BE%8E%E6%94%B6%E5%89%B2%E5%85%A8%E7%90%83%E8%99%9A%E6%8B%9F%E8%B4%A7%E5%B8%81%E8%B5%84%E4%BA%A7?type=general",
            hot_value: "11352263",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015/oEBw31QAGZAL4IykUc7sfPe8pbGGBCOQ4O4Ttf~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=dg5YRlH76jUVpGpH1Y9fx5IU2K8%3D&from=3218412987",
                hot_value: Int32("11352263"),
                label: Int32("1"),
                sentence_id: "2412021",
                video_count: Int32("1"),
                view_count: Int32("63423901")
            }
        },
        {
            index: Int32("2"),
            title: "正月初十十全十美",
            url: "https://www.douyin.com/search/%E6%AD%A3%E6%9C%88%E5%88%9D%E5%8D%81%E5%8D%81%E5%85%A8%E5%8D%81%E7%BE%8E?type=general",
            hot_value: "11175962",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/osIgAIPL7YRgTAueeesP0XwXhKdGBCLRGTyBvm~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=j2%2F%2BlGLJdwoEYXJAbEsijd%2BBvro%3D&from=3218412987",
                hot_value: Int32("11175962"),
                label: Int32("17"),
                sentence_id: "2411895",
                video_count: Int32("4"),
                view_count: Int32("62270509")
            }
        },
        {
            index: Int32("3"),
            title: "全国铁路春运发送旅客破3亿人次",
            url: "https://www.douyin.com/search/%E5%85%A8%E5%9B%BD%E9%93%81%E8%B7%AF%E6%98%A5%E8%BF%90%E5%8F%91%E9%80%81%E6%97%85%E5%AE%A2%E7%A0%B43%E4%BA%BF%E4%BA%BA%E6%AC%A1?type=general",
            hot_value: "11117276",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/o0NCESrng9s9AQC1pvQMOEFQAEAeCrfvBODID8~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=YsjkDz5Rg692Ttgefx9sIbpDbUQ%3D&from=3218412987",
                hot_value: Int32("11117276"),
                label: Int32("3"),
                sentence_id: "2411828",
                video_count: Int32("1"),
                view_count: Int32("63884446")
            }
        },
        {
            index: Int32("4"),
            title: "国投白银LOF补偿方案正式启动",
            url: "https://www.douyin.com/search/%E5%9B%BD%E6%8A%95%E7%99%BD%E9%93%B6LOF%E8%A1%A5%E5%81%BF%E6%96%B9%E6%A1%88%E6%AD%A3%E5%BC%8F%E5%90%AF%E5%8A%A8?type=general",
            hot_value: "10859450",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/o4QMp9enBA9mLtfOAgWYfJQMx8teE7kQEHIpfg~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=NvNCEi05wRLZbAtvT%2Fqx%2B8ygpOk%3D&from=3218412987",
                hot_value: Int32("10859450"),
                label: Int32("1"),
                sentence_id: "2411966",
                video_count: Int32("4"),
                view_count: Int32("64876695")
            }
        },
        {
            index: Int32("5"),
            title: "古巴称与美籍快艇交火致4死6伤",
            url: "https://www.douyin.com/search/%E5%8F%A4%E5%B7%B4%E7%A7%B0%E4%B8%8E%E7%BE%8E%E7%B1%8D%E5%BF%AB%E8%89%87%E4%BA%A4%E7%81%AB%E8%87%B44%E6%AD%BB6%E4%BC%A4?type=general",
            hot_value: "10205217",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/oEPf6MeTQLMhAWNUqQYQnAEh8fgfIIMeHQ78th~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=GB2zG757xuecgSYii5i9JMpbAuQ%3D&from=3218412987",
                hot_value: Int32("10205217"),
                label: Int32("3"),
                sentence_id: "2411885",
                video_count: Int32("4"),
                view_count: Int32("59905558")
            }
        },
        {
            index: Int32("6"),
            title: "雪饼猴的遗憾",
            url: "https://www.douyin.com/search/%E9%9B%AA%E9%A5%BC%E7%8C%B4%E7%9A%84%E9%81%97%E6%86%BE?type=general",
            hot_value: "10191258",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/o8PAoCIVPvGT7iApkuoyL4eBeTEFkTQBrfQ7lO~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=a8C9MNXqXr1zHKiqmd%2FdBNK3U7o%3D&from=3218412987",
                hot_value: Int32("10191258"),
                label: Int32("0"),
                sentence_id: "2411829",
                video_count: Int32("1"),
                view_count: Int32("57060388")
            }
        },
        {
            index: Int32("7"),
            title: "网传医院有安乐死胶囊系谣言",
            url: "https://www.douyin.com/search/%E7%BD%91%E4%BC%A0%E5%8C%BB%E9%99%A2%E6%9C%89%E5%AE%89%E4%B9%90%E6%AD%BB%E8%83%B6%E5%9B%8A%E7%B3%BB%E8%B0%A3%E8%A8%80?type=general",
            hot_value: "8615808",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-i-dy/ef3c737e242140ffa09fa312556d5fbf~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=tc9wuV4aclJ6h2L%2FXBXaVfBsJuE%3D&from=3218412987",
                hot_value: Int32("8615808"),
                label: Int32("16"),
                sentence_id: "2411704",
                video_count: Int32("2"),
                view_count: Int32("51015325")
            }
        },
        {
            index: Int32("8"),
            title: "命中注定了让你遇见我",
            url: "https://www.douyin.com/search/%E5%91%BD%E4%B8%AD%E6%B3%A8%E5%AE%9A%E4%BA%86%E8%AE%A9%E4%BD%A0%E9%81%87%E8%A7%81%E6%88%91?type=general",
            hot_value: "7790996",
            extra: {
                cover: "https://p9-sign.douyinpic.com/tos-cn-i-0813c001/osMpud74AAAoA96kgEFem3ND7f52mv9EAACCbI~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=dpm9WF2xMqFD5fLb9dKFwNC2whA%3D&from=3218412987",
                hot_value: Int32("7790996"),
                label: Int32("9"),
                sentence_id: "2411789",
                video_count: Int32("7"),
                view_count: Int32("33046526")
            }
        },
        {
            index: Int32("9"),
            title: "过年后回家的留守猫",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E5%90%8E%E5%9B%9E%E5%AE%B6%E7%9A%84%E7%95%99%E5%AE%88%E7%8C%AB?type=general",
            hot_value: "7770463",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-i-0813/oQrdYpafEsUTAFVC1ACEAgAN3rAnCCDiAIif95~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=RlXZ7N3vFNC5icPqnNRMTbg5zK8%3D&from=3218412987",
                hot_value: Int32("7770463"),
                label: Int32("9"),
                sentence_id: "2410740",
                video_count: Int32("10"),
                view_count: Int32("38174993")
            }
        },
        {
            index: Int32("10"),
            title: "马年就是快啊",
            url: "https://www.douyin.com/search/%E9%A9%AC%E5%B9%B4%E5%B0%B1%E6%98%AF%E5%BF%AB%E5%95%8A?type=general",
            hot_value: "7751831",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/o06eYriEQz9EDQyI2BFpAuMDwsnDDEgKfrnAw1~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=M5%2FZPBRnuBc4C3B5OvAhzn%2FVtGA%3D&from=3218412987",
                hot_value: Int32("7751831"),
                label: Int32("0"),
                sentence_id: "2411893",
                video_count: Int32("3"),
                view_count: Int32("30360934")
            }
        },
        {
            index: Int32("11"),
            title: "唐宫奇案启动法律程序",
            url: "https://www.douyin.com/search/%E5%94%90%E5%AE%AB%E5%A5%87%E6%A1%88%E5%90%AF%E5%8A%A8%E6%B3%95%E5%BE%8B%E7%A8%8B%E5%BA%8F?type=general",
            hot_value: "7734724",
            extra: {
                cover: "https://p9-sign.douyinpic.com/tos-cn-i-0813/owjBUeS67AW7GPAgAAVIAbEaWBPLQfexTZ0NAJ~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=F4qBpGXW8b55fr84RI9zPtNpN7k%3D&from=3218412987",
                hot_value: Int32("7734724"),
                label: Int32("8"),
                sentence_id: "2411600",
                video_count: Int32("2"),
                view_count: Int32("29608519")
            }
        },
        {
            index: Int32("12"),
            title: "麻辣拌界有自己的史铁生",
            url: "https://www.douyin.com/search/%E9%BA%BB%E8%BE%A3%E6%8B%8C%E7%95%8C%E6%9C%89%E8%87%AA%E5%B7%B1%E7%9A%84%E5%8F%B2%E9%93%81%E7%94%9F?type=general",
            hot_value: "7724417",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/o8AAFngem1pQfBvWq8DqcQOyCnp9EZFgGcbAC3~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=lyXmrtKGrX1WD8OncGkZCotfUD8%3D&from=3218412987",
                hot_value: Int32("7724417"),
                label: Int32("3"),
                sentence_id: "2411843",
                video_count: Int32("3"),
                view_count: Int32("29856681")
            }
        },
        {
            index: Int32("13"),
            title: "县委书记抖音号成“民情留言板”",
            url: "https://www.douyin.com/search/%E5%8E%BF%E5%A7%94%E4%B9%A6%E8%AE%B0%E6%8A%96%E9%9F%B3%E5%8F%B7%E6%88%90%E2%80%9C%E6%B0%91%E6%83%85%E7%95%99%E8%A8%80%E6%9D%BF%E2%80%9D?type=general",
            hot_value: "7720010",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/ok6OTBQKkBGkAeApI4sBCgJ46ELd7OkIfsnie2~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=84dquPifMcAVFmcfTnTuXIoGsws%3D&from=3218412987",
                hot_value: Int32("7720010"),
                label: Int32("0"),
                sentence_id: "2411692",
                video_count: Int32("3"),
                view_count: Int32("27308764")
            }
        },
        {
            index: Int32("14"),
            title: "韩振也摇起来了",
            url: "https://www.douyin.com/search/%E9%9F%A9%E6%8C%AF%E4%B9%9F%E6%91%87%E8%B5%B7%E6%9D%A5%E4%BA%86?type=general",
            hot_value: "7711570",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/ooI29p8AuBoIIw94lMQAsFEEaDDfvnFltfGvrn~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=sXNHCx7Fl%2BK6FFimUgGxs3EIkpw%3D&from=3218412987",
                hot_value: Int32("7711570"),
                label: Int32("17"),
                sentence_id: "2411853",
                video_count: Int32("1"),
                view_count: Int32("26085599")
            }
        },
        {
            index: Int32("15"),
            title: "瞿桦把结婚证当护妻符",
            url: "https://www.douyin.com/search/%E7%9E%BF%E6%A1%A6%E6%8A%8A%E7%BB%93%E5%A9%9A%E8%AF%81%E5%BD%93%E6%8A%A4%E5%A6%BB%E7%AC%A6?type=general",
            hot_value: "7703610",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/osBd9YDlncsfvgQ79TdnonVEEk7FQApBEQwAen~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=OhRzkivKTirGiTKpLQyV%2BmbKfF8%3D&from=3218412987",
                hot_value: Int32("7703610"),
                label: Int32("8"),
                sentence_id: "2411774",
                video_count: Int32("1"),
                view_count: Int32("21309553")
            }
        },
        {
            index: Int32("16"),
            title: "课堂上的风吹到了橘子洲头",
            url: "https://www.douyin.com/search/%E8%AF%BE%E5%A0%82%E4%B8%8A%E7%9A%84%E9%A3%8E%E5%90%B9%E5%88%B0%E4%BA%86%E6%A9%98%E5%AD%90%E6%B4%B2%E5%A4%B4?type=general",
            hot_value: "7702089",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/ogAIeFFtonM5Duwo9fMBrgApwoEMEclQNpotQk~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=o38O%2B5q1H%2Bp5BztxDY3p5IrKVy8%3D&from=3218412987",
                hot_value: Int32("7702089"),
                label: Int32("0"),
                sentence_id: "2411686",
                video_count: Int32("1"),
                view_count: Int32("23767488")
            }
        },
        {
            index: Int32("17"),
            title: "开学的味道我知道",
            url: "https://www.douyin.com/search/%E5%BC%80%E5%AD%A6%E7%9A%84%E5%91%B3%E9%81%93%E6%88%91%E7%9F%A5%E9%81%93?type=general",
            hot_value: "7697140",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/oQBfBYyhwmtmTf34DApUJgmf2z2caAIYgAHGIf~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=P1QItLc2KaMWhYKGheVYFcjwh8c%3D&from=3218412987",
                hot_value: Int32("7697140"),
                label: Int32("9"),
                sentence_id: "2411634",
                video_count: Int32("10"),
                view_count: Int32("22059768")
            }
        },
        {
            index: Int32("18"),
            title: "中国男篮公布客战日本12人名单",
            url: "https://www.douyin.com/search/%E4%B8%AD%E5%9B%BD%E7%94%B7%E7%AF%AE%E5%85%AC%E5%B8%83%E5%AE%A2%E6%88%98%E6%97%A5%E6%9C%AC12%E4%BA%BA%E5%90%8D%E5%8D%95?type=general",
            hot_value: "7694298",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015/o4TBcgWt7JTAcpfhCeIECLPB7BFG5AFE2QeZIm~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=VxXlyw5URPgYNHLNzlsTpTUBzvo%3D&from=3218412987",
                hot_value: Int32("7694298"),
                label: Int32("0"),
                sentence_id: "2411803",
                video_count: Int32("3"),
                view_count: Int32("19515829")
            }
        },
        {
            index: Int32("19"),
            title: "来都来了 吃个轻轨再走吧",
            url: "https://www.douyin.com/search/%E6%9D%A5%E9%83%BD%E6%9D%A5%E4%BA%86%20%E5%90%83%E4%B8%AA%E8%BD%BB%E8%BD%A8%E5%86%8D%E8%B5%B0%E5%90%A7?type=general",
            hot_value: "7692350",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015/oUaoIIFWEDEese3dBGDAI9Oz7xTAaCWB4sEOf8~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=0XF68bX78u25AtK8G5rSNec%2BRAA%3D&from=3218412987",
                hot_value: Int32("7692350"),
                label: Int32("1"),
                sentence_id: "2411973",
                video_count: Int32("2"),
                view_count: Int32("18884382")
            }
        },
        {
            index: Int32("20"),
            title: "三角洲行动干员专属bgm盘点",
            url: "https://www.douyin.com/search/%E4%B8%89%E8%A7%92%E6%B4%B2%E8%A1%8C%E5%8A%A8%E5%B9%B2%E5%91%98%E4%B8%93%E5%B1%9Ebgm%E7%9B%98%E7%82%B9?type=general",
            hot_value: "7691133",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/ocBAAVfnxFu8TAVDIpEDsPfhIW2TgAbwACd4O9~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=crx67FeRacLCz9FY0HspleRHV%2Bc%3D&from=3218412987",
                hot_value: Int32("7691133"),
                label: Int32("3"),
                sentence_id: "2411473",
                video_count: Int32("2"),
                view_count: Int32("17686437")
            }
        },
        {
            index: Int32("21"),
            title: "白鹿：下一个角色见",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%EF%BC%9A%E4%B8%8B%E4%B8%80%E4%B8%AA%E8%A7%92%E8%89%B2%E8%A7%81?type=general",
            hot_value: "7689883",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/ooae9tO4pQDiAxA70BnF2MGEQ1DDVLAxogf9lN~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=Va4qyR5ydapOx2EcnT0dgkAJ%2B9c%3D&from=3218412987",
                hot_value: Int32("7689883"),
                label: Int32("3"),
                sentence_id: "2411726",
                video_count: Int32("1"),
                view_count: Int32("15203594")
            }
        },
        {
            index: Int32("22"),
            title: "好好的时光里各有各的幸福",
            url: "https://www.douyin.com/search/%E5%A5%BD%E5%A5%BD%E7%9A%84%E6%97%B6%E5%85%89%E9%87%8C%E5%90%84%E6%9C%89%E5%90%84%E7%9A%84%E5%B9%B8%E7%A6%8F?type=general",
            hot_value: "7689128",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015/osenNQ5QDbbscBy3gEf0AnESNF9QcpAAR2a99d~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=6KCf8rC%2FG7SoSTWJIJ%2B38Qy28Z8%3D&from=3218412987",
                hot_value: Int32("7689128"),
                label: Int32("5"),
                sentence_id: "2411588",
                video_count: Int32("3"),
                view_count: Int32("13858205")
            }
        },
        {
            index: Int32("23"),
            title: "AI帮你选对发型",
            url: "https://www.douyin.com/search/AI%E5%B8%AE%E4%BD%A0%E9%80%89%E5%AF%B9%E5%8F%91%E5%9E%8B?type=general",
            hot_value: "7685690",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-i-0813c001/ogABAuV7CjTQeERAjEGzkIh4GOO7IrLAAftBeO~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=aTvXWvc0u98p8jZ3%2FmxogvTt%2Fss%3D&from=3218412987",
                hot_value: Int32("7685690"),
                label: Int32("9"),
                sentence_id: "2411301",
                video_count: Int32("10"),
                view_count: Int32("14627521")
            }
        },
        {
            index: Int32("24"),
            title: "古风回眸一眼万年",
            url: "https://www.douyin.com/search/%E5%8F%A4%E9%A3%8E%E5%9B%9E%E7%9C%B8%E4%B8%80%E7%9C%BC%E4%B8%87%E5%B9%B4?type=general",
            hot_value: "7677658",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015c000-ce/oYpwnnaErBeEuAF9iEgItWxDomAwwTfC0j6DEx~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=Rvgv2fAbP8zZ5o0%2FuOv9J%2BPUOeQ%3D&from=3218412987",
                hot_value: Int32("7677658"),
                label: Int32("9"),
                sentence_id: "2411637",
                video_count: Int32("10"),
                view_count: Int32("11328019")
            }
        },
        {
            index: Int32("25"),
            title: "张博闻新歌烟火",
            url: "https://www.douyin.com/search/%E5%BC%A0%E5%8D%9A%E9%97%BB%E6%96%B0%E6%AD%8C%E7%83%9F%E7%81%AB?type=general",
            hot_value: "7676131",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/oMVeYpPJEH3tAFUUNCeIEwE1XsRnC8DpAQlf9G~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=FRjXm1xn4fBkArPyuw97uhDAk3k%3D&from=3218412987",
                hot_value: Int32("7676131"),
                label: Int32("3"),
                sentence_id: "2411869",
                video_count: Int32("1"),
                view_count: Int32("10682722")
            }
        },
        {
            index: Int32("26"),
            title: "加入抖音镖人护镖小队",
            url: "https://www.douyin.com/search/%E5%8A%A0%E5%85%A5%E6%8A%96%E9%9F%B3%E9%95%96%E4%BA%BA%E6%8A%A4%E9%95%96%E5%B0%8F%E9%98%9F?type=general",
            hot_value: "7671435",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015/oA8TYK78BsMOe4fQq2Xnxg7qB4frgACNNVHaqA~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=f0HPszsch8p13CoLlYaOhiacRb0%3D&from=3218412987",
                hot_value: Int32("7671435"),
                label: Int32("8"),
                sentence_id: "2411771",
                video_count: Int32("10"),
                view_count: Int32("10032277")
            }
        },
        {
            index: Int32("27"),
            title: "王天辰郭晓婷新剧姐狗文学",
            url: "https://www.douyin.com/search/%E7%8E%8B%E5%A4%A9%E8%BE%B0%E9%83%AD%E6%99%93%E5%A9%B7%E6%96%B0%E5%89%A7%E5%A7%90%E7%8B%97%E6%96%87%E5%AD%A6?type=general",
            hot_value: "7666952",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/o0y7QaCnpGA4ltwKrSLyB7TE0B5ASC7PQeekeI~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=%2Bj2drWPdCFJX6neoOlfDVtxxwkU%3D&from=3218412987",
                hot_value: Int32("7666952"),
                label: Int32("3"),
                sentence_id: "2411606",
                video_count: Int32("1"),
                view_count: Int32("8440803")
            }
        },
        {
            index: Int32("28"),
            title: "就说看时装周真能学到东西",
            url: "https://www.douyin.com/search/%E5%B0%B1%E8%AF%B4%E7%9C%8B%E6%97%B6%E8%A3%85%E5%91%A8%E7%9C%9F%E8%83%BD%E5%AD%A6%E5%88%B0%E4%B8%9C%E8%A5%BF?type=general",
            hot_value: "7665579",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/oYi8tcEIEBATMhMfL6FGZUmo4UjBRBAaDCe7Cf~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=1ruz5daPCDXZngCe9IQ7LNiiVvs%3D&from=3218412987",
                hot_value: Int32("7665579"),
                label: Int32("5"),
                sentence_id: "2411247",
                video_count: Int32("3"),
                view_count: Int32("6072927")
            }
        },
        {
            index: Int32("29"),
            title: "黄明昊章昊 成功人士成功会面",
            url: "https://www.douyin.com/search/%E9%BB%84%E6%98%8E%E6%98%8A%E7%AB%A0%E6%98%8A%20%E6%88%90%E5%8A%9F%E4%BA%BA%E5%A3%AB%E6%88%90%E5%8A%9F%E4%BC%9A%E9%9D%A2?type=general",
            hot_value: "7662531",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/oYEbQndfog0ItaA92gnphIFFM2kD58wEAViAeB~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=XM6BoFYuzfKLnt8zXpV08E2%2FewM%3D&from=3218412987",
                hot_value: Int32("7662531"),
                label: Int32("3"),
                sentence_id: "2411687",
                video_count: Int32("1"),
                view_count: Int32("4464568")
            }
        },
        {
            index: Int32("30"),
            title: "张艺兴阴天在不开灯的房间",
            url: "https://www.douyin.com/search/%E5%BC%A0%E8%89%BA%E5%85%B4%E9%98%B4%E5%A4%A9%E5%9C%A8%E4%B8%8D%E5%BC%80%E7%81%AF%E7%9A%84%E6%88%BF%E9%97%B4?type=general",
            hot_value: "7662350",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-i-0813/oQAeZLMuAz87LGnmQCkBzYAZEfIBPTbGAAE9Ie~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=naN5vdc8zYFLo8WZny8BQfmPDaQ%3D&from=3218412987",
                hot_value: Int32("7662350"),
                label: Int32("3"),
                sentence_id: "2411776",
                video_count: Int32("1"),
                view_count: Int32("4036320")
            }
        },
        {
            index: Int32("31"),
            title: "周翊然包上恩新剧双向沦陷",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E6%96%B0%E5%89%A7%E5%8F%8C%E5%90%91%E6%B2%A6%E9%99%B7?type=general",
            hot_value: "7661897",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015/oQ7kTBveAevQgdYTiMGXQr5PQCI8Q1Qe7AMZBB~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=h%2FdoO2NWVc3Ly%2FLR2lea5Hz%2Fbtg%3D&from=3218412987",
                hot_value: Int32("7661897"),
                label: Int32("5"),
                sentence_id: "2411331",
                video_count: Int32("3"),
                view_count: Int32("2706986")
            }
        },
        {
            index: Int32("32"),
            title: "蔡徐坤滑动歌单一键变装",
            url: "https://www.douyin.com/search/%E8%94%A1%E5%BE%90%E5%9D%A4%E6%BB%91%E5%8A%A8%E6%AD%8C%E5%8D%95%E4%B8%80%E9%94%AE%E5%8F%98%E8%A3%85?type=general",
            hot_value: "7661224",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015c000-ce/oINnDf65AEGeQeJW6CpwFCO9Is9pAxAusE97vc~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=%2BlGnJZt0zbNOJ5Gt7kX00q72eLU%3D&from=3218412987",
                hot_value: Int32("7661224"),
                label: Int32("17"),
                sentence_id: "2411341",
                video_count: Int32("1"),
                view_count: Int32("1384432")
            }
        },
        {
            index: Int32("33"),
            title: "茶花开了该回家了",
            url: "https://www.douyin.com/search/%E8%8C%B6%E8%8A%B1%E5%BC%80%E4%BA%86%E8%AF%A5%E5%9B%9E%E5%AE%B6%E4%BA%86?type=general",
            hot_value: "7660174",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/ocABFQJd1XTQ8CaB0eMkfQ5IEOI7QFXAuQfByi~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=fM1%2Btc6EOQSR8Lkm8xBiIjMAT6w%3D&from=3218412987",
                hot_value: Int32("7660174"),
                label: Int32("17"),
                sentence_id: "2411173",
                video_count: Int32("3"),
                view_count: Int32("2296115")
            }
        },
        {
            index: Int32("34"),
            title: "老夫老妻拍照没必要太正常",
            url: "https://www.douyin.com/search/%E8%80%81%E5%A4%AB%E8%80%81%E5%A6%BB%E6%8B%8D%E7%85%A7%E6%B2%A1%E5%BF%85%E8%A6%81%E5%A4%AA%E6%AD%A3%E5%B8%B8?type=general",
            hot_value: "7646587",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/ospWojeRiBjIvAF98E2Q0tVDanANwQfEVJ8DEU~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=7eu9DymmYjRx4zJZVGDPd5JdxEg%3D&from=3218412987",
                hot_value: Int32("7646587"),
                label: Int32("3"),
                sentence_id: "2411860",
                video_count: Int32("1"),
                view_count: Int32("546890")
            }
        },
        {
            index: Int32("35"),
            title: "小满晓丹结束异地恋",
            url: "https://www.douyin.com/search/%E5%B0%8F%E6%BB%A1%E6%99%93%E4%B8%B9%E7%BB%93%E6%9D%9F%E5%BC%82%E5%9C%B0%E6%81%8B?type=general",
            hot_value: "7640760",
            extra: {
                cover: "https://p9-sign.douyinpic.com/tos-cn-p-0015/osnbXADdIFATIkCOfAEEG5BdBjeXf7gdToOiA9~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=jML5tWbJ5hRJLnxHbAH6IjNajMA%3D&from=3218412987",
                hot_value: Int32("7640760"),
                label: Int32("11"),
                sentence_id: "2411224",
                video_count: Int32("1"),
                view_count: Int32("4912705")
            }
        },
        {
            index: Int32("36"),
            title: "当你有一个预判型孩子",
            url: "https://www.douyin.com/search/%E5%BD%93%E4%BD%A0%E6%9C%89%E4%B8%80%E4%B8%AA%E9%A2%84%E5%88%A4%E5%9E%8B%E5%AD%A9%E5%AD%90?type=general",
            hot_value: "7637901",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/oITOu6w9QLfCDmuBQ2edhJASI7Fv9QfxRgdDaE~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=FPLRG5%2BuMe3pVZzKSMcMFBUvBM0%3D&from=3218412987",
                hot_value: Int32("7637901"),
                label: Int32("0"),
                sentence_id: "2411079",
                video_count: Int32("1"),
                view_count: Int32("6536764")
            }
        },
        {
            index: Int32("37"),
            title: "我陈平安唯有一剑",
            url: "https://www.douyin.com/search/%E6%88%91%E9%99%88%E5%B9%B3%E5%AE%89%E5%94%AF%E6%9C%89%E4%B8%80%E5%89%91?type=general",
            hot_value: "7636565",
            extra: {
                cover: "https://p11-sign.douyinpic.com/tos-cn-p-0015/oMdxgnDGLQpfFa4RUNfB9PGgFp0mlZA4AEAMHQ~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=Fs0iRR1OYR2cOXDkoDS6XJxXfCQ%3D&from=3218412987",
                hot_value: Int32("7636565"),
                label: Int32("0"),
                sentence_id: "2410790",
                video_count: Int32("4"),
                view_count: Int32("10791951")
            }
        },
        {
            index: Int32("38"),
            title: "豌豆公主我终于理解你了",
            url: "https://www.douyin.com/search/%E8%B1%8C%E8%B1%86%E5%85%AC%E4%B8%BB%E6%88%91%E7%BB%88%E4%BA%8E%E7%90%86%E8%A7%A3%E4%BD%A0%E4%BA%86?type=general",
            hot_value: "7634269",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-i-0813c000-ce/o49CZE36AvAIkAvpkCnFE7FmEC1f3AdYvwDLAf~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=VXxvz%2FqwVWP2TRDaTqxdLAJ4KtE%3D&from=3218412987",
                hot_value: Int32("7634269"),
                label: Int32("0"),
                sentence_id: "2410391",
                video_count: Int32("10"),
                view_count: Int32("8753605")
            }
        },
        {
            index: Int32("39"),
            title: "叶经理之前就点过张弛",
            url: "https://www.douyin.com/search/%E5%8F%B6%E7%BB%8F%E7%90%86%E4%B9%8B%E5%89%8D%E5%B0%B1%E7%82%B9%E8%BF%87%E5%BC%A0%E5%BC%9B?type=general",
            hot_value: "7630962",
            extra: {
                cover: "https://p9-sign.douyinpic.com/tos-cn-p-0015c000-ce/oUtP5GNRgAQBS2DBaJeIGCWz8Qc7geLpT0DMwe~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=OeiVzu08ErOrt8p2WgOZURFRi%2BQ%3D&from=3218412987",
                hot_value: Int32("7630962"),
                label: Int32("0"),
                sentence_id: "2411139",
                video_count: Int32("1"),
                view_count: Int32("9920615")
            }
        },
        {
            index: Int32("40"),
            title: "酥心糖跨国热心接力开始了",
            url: "https://www.douyin.com/search/%E9%85%A5%E5%BF%83%E7%B3%96%E8%B7%A8%E5%9B%BD%E7%83%AD%E5%BF%83%E6%8E%A5%E5%8A%9B%E5%BC%80%E5%A7%8B%E4%BA%86?type=general",
            hot_value: "7628151",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/oIZIbIKAPQ4QSp0bAanIyP2T8CWjiiZlI0B9B~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=gx%2BzQdIR6iSC5qvGEk0O1H9xPQ8%3D&from=3218412987",
                hot_value: Int32("7628151"),
                label: Int32("0"),
                sentence_id: "2411547",
                video_count: Int32("3"),
                view_count: Int32("6691540")
            }
        },
        {
            index: Int32("41"),
            title: "我们是天下第一好",
            url: "https://www.douyin.com/search/%E6%88%91%E4%BB%AC%E6%98%AF%E5%A4%A9%E4%B8%8B%E7%AC%AC%E4%B8%80%E5%A5%BD?type=general",
            hot_value: "7627851",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/oUIBA9rPcADi6iPPacwhZBmcHaiEsOMM2Sqqg~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=HRxHuqY%2BnMLFVUfXirJtFEsbn3s%3D&from=3218412987",
                hot_value: Int32("7627851"),
                label: Int32("0"),
                sentence_id: "2410316",
                video_count: Int32("10"),
                view_count: Int32("8651310")
            }
        },
        {
            index: Int32("42"),
            title: "谁懂许凯这个男友视角",
            url: "https://www.douyin.com/search/%E8%B0%81%E6%87%82%E8%AE%B8%E5%87%AF%E8%BF%99%E4%B8%AA%E7%94%B7%E5%8F%8B%E8%A7%86%E8%A7%92?type=general",
            hot_value: "7627258",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/okfgAlegHYkBEeMoVvv3HfgD7YeF4NA0tJIZpQ~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=u9i75SOIck4rLJ6JN13Dg4w%2FDZU%3D&from=3218412987",
                hot_value: Int32("7627258"),
                label: Int32("0"),
                sentence_id: "2411677",
                video_count: Int32("1"),
                view_count: Int32("11307761")
            }
        },
        {
            index: Int32("43"),
            title: "岁月有情时铁三角神仙友情",
            url: "https://www.douyin.com/search/%E5%B2%81%E6%9C%88%E6%9C%89%E6%83%85%E6%97%B6%E9%93%81%E4%B8%89%E8%A7%92%E7%A5%9E%E4%BB%99%E5%8F%8B%E6%83%85?type=general",
            hot_value: "7625231",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/oAdkeFC7EDTWOQBa5AasA6rqIfL0E6BEk3IpeC~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=6J7Sd276Mq3tSoe8npZmka9Un7M%3D&from=3218412987",
                hot_value: Int32("7625231"),
                label: Int32("5"),
                sentence_id: "2411227",
                video_count: Int32("3"),
                view_count: Int32("4122291")
            }
        },
        {
            index: Int32("44"),
            title: "王鸥 郝小姐真的尽力啦",
            url: "https://www.douyin.com/search/%E7%8E%8B%E9%B8%A5%20%E9%83%9D%E5%B0%8F%E5%A7%90%E7%9C%9F%E7%9A%84%E5%B0%BD%E5%8A%9B%E5%95%A6?type=general",
            hot_value: "7622054",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015c000-ce/o83ViiEQIEwpannfFjFneIURAs4DjAANDBo9Co~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=1FE7GJzfUS0fC1qWVYRUzOmwhjM%3D&from=3218412987",
                hot_value: Int32("7622054"),
                label: Int32("0"),
                sentence_id: "2411583",
                video_count: Int32("1"),
                view_count: Int32("5314294")
            }
        },
        {
            index: Int32("45"),
            title: "歌手徐浩勇闯团播",
            url: "https://www.douyin.com/search/%E6%AD%8C%E6%89%8B%E5%BE%90%E6%B5%A9%E5%8B%87%E9%97%AF%E5%9B%A2%E6%92%AD?type=general",
            hot_value: "7620153",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/osowZSriAb8Aaeop9P6BEb4h4EIIEBFdSmYnfD~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=ArTQ1H%2BqvMHoB2d2Cdn9HDwKKao%3D&from=3218412987",
                hot_value: Int32("7620153"),
                label: Int32("0"),
                sentence_id: "2411580",
                video_count: Int32("2"),
                view_count: Int32("6661190")
            }
        },
        {
            index: Int32("46"),
            title: "闵熙珍放弃255亿韩元赔偿",
            url: "https://www.douyin.com/search/%E9%97%B5%E7%86%99%E7%8F%8D%E6%94%BE%E5%BC%83255%E4%BA%BF%E9%9F%A9%E5%85%83%E8%B5%94%E5%81%BF?type=general",
            hot_value: "7619839",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-i-dy/3b5dc3c841c742729f2b654e315a529a~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=BLTFyoIbRzRbPF2Fgw2yhoXNnP0%3D&from=3218412987",
                hot_value: Int32("7619839"),
                label: Int32("0"),
                sentence_id: "2411367",
                video_count: Int32("1"),
                view_count: Int32("5824475")
            }
        },
        {
            index: Int32("47"),
            title: "360天换来的5天热闹梦",
            url: "https://www.douyin.com/search/360%E5%A4%A9%E6%8D%A2%E6%9D%A5%E7%9A%845%E5%A4%A9%E7%83%AD%E9%97%B9%E6%A2%A6?type=general",
            hot_value: "7617771",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/o8M9iuagB8AZCpZ8ZrXQPCiIApjPVOvEnmC7h~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=J0KK1UyxJUnwNRmk8%2BYKLXRZ2sE%3D&from=3218412987",
                hot_value: Int32("7617771"),
                label: Int32("0"),
                sentence_id: "2410617",
                video_count: Int32("10"),
                view_count: Int32("10155293")
            }
        },
        {
            index: Int32("48"),
            title: "刘世豪被做局委屈巴巴",
            url: "https://www.douyin.com/search/%E5%88%98%E4%B8%96%E8%B1%AA%E8%A2%AB%E5%81%9A%E5%B1%80%E5%A7%94%E5%B1%88%E5%B7%B4%E5%B7%B4?type=general",
            hot_value: "7614424",
            extra: {
                cover: "https://p3-sign.douyinpic.com/tos-cn-p-0015/oo0ARKinSIBh6yCAeUvgflivpdI09XQADB3ZnB~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=Ua9OWeGtlqYJnC9lV%2Fliceu7rsE%3D&from=3218412987",
                hot_value: Int32("7614424"),
                label: Int32("0"),
                sentence_id: "2411387",
                video_count: Int32("1"),
                view_count: Int32("9678461")
            }
        },
        {
            index: Int32("49"),
            title: "王玉雯今天是甜妹",
            url: "https://www.douyin.com/search/%E7%8E%8B%E7%8E%89%E9%9B%AF%E4%BB%8A%E5%A4%A9%E6%98%AF%E7%94%9C%E5%A6%B9?type=general",
            hot_value: "7613839",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/ogPUgnoUDQ0Wuen9AXFHej9K2CfjpDEQEsw7An~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=z2G49lTBdDeDYCiyOVybyFB4tOQ%3D&from=3218412987",
                hot_value: Int32("7613839"),
                label: Int32("0"),
                sentence_id: "2411340",
                video_count: Int32("1"),
                view_count: Int32("6775805")
            }
        },
        {
            index: Int32("50"),
            title: "你知道的我从小就跟着你了",
            url: "https://www.douyin.com/search/%E4%BD%A0%E7%9F%A5%E9%81%93%E7%9A%84%E6%88%91%E4%BB%8E%E5%B0%8F%E5%B0%B1%E8%B7%9F%E7%9D%80%E4%BD%A0%E4%BA%86?type=general",
            hot_value: "7613274",
            extra: {
                cover: "https://p26-sign.douyinpic.com/tos-cn-p-0015c000-ce/oQCaADSnAF6eRAQBIpED3FfoQ1slwwxUEedDA9~noop.jpeg?lk3s=bfd515bb&x-expires=1772092800&x-signature=C7PfwU1g2IS7pOjkMKay5%2FUF8oc%3D&from=3218412987",
                hot_value: Int32("7613274"),
                label: Int32("0"),
                sentence_id: "2410480",
                video_count: Int32("10"),
                view_count: Int32("6360730")
            }
        }
    ],
    created_at: ISODate("2026-02-26T10:29:23.505Z")
} ]);

// ----------------------------
// Collection structure for hot_news_main
// ----------------------------
db.getCollection("hot_news_main").drop();
db.createCollection("hot_news_main");

// ----------------------------
// Documents of hot_news_main
// ----------------------------
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("69840872b4480d4affb51e36"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "习近平同普京举行视频会晤",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E6%99%AE%E4%BA%AC%E4%B8%BE%E8%A1%8C%E8%A7%86%E9%A2%91%E4%BC%9A%E6%99%A4"
        },
        {
            index: Int32("2"),
            title: "习近平同特朗普通电话",
            hot: "1195.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E7%89%B9%E6%9C%97%E6%99%AE%E9%80%9A%E7%94%B5%E8%AF%9D"
        },
        {
            index: Int32("3"),
            title: "各地春节年俗地图",
            hot: "1136.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("4"),
            title: "农业综合生产能力迈上新台阶",
            hot: "1118万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E7%94%9F%E4%BA%A7%E8%83%BD%E5%8A%9B%E8%BF%88%E4%B8%8A%E6%96%B0%E5%8F%B0%E9%98%B6"
        },
        {
            index: Int32("5"),
            title: "霉豆腐的风还是吹到了蛋糕界",
            hot: "1075.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%9C%89%E8%B1%86%E8%85%90%E7%9A%84%E9%A3%8E%E8%BF%98%E6%98%AF%E5%90%B9%E5%88%B0%E4%BA%86%E8%9B%8B%E7%B3%95%E7%95%8C"
        },
        {
            index: Int32("6"),
            title: "过年氛围提前搞起来了",
            hot: "1020.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("7"),
            title: "粉彩风和立春一起来了",
            hot: "1019.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%B2%89%E5%BD%A9%E9%A3%8E%E5%92%8C%E7%AB%8B%E6%98%A5%E4%B8%80%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("8"),
            title: "浓眉被交易至奇才",
            hot: "911.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "882.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "这才是跨火盆的满分答案",
            hot: "864.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%99%E6%89%8D%E6%98%AF%E8%B7%A8%E7%81%AB%E7%9B%86%E7%9A%84%E6%BB%A1%E5%88%86%E7%AD%94%E6%A1%88"
        },
        {
            index: Int32("11"),
            title: "一个28岁青年的沙漠梦想",
            hot: "841.6万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%B8%AA28%E5%B2%81%E9%9D%92%E5%B9%B4%E7%9A%84%E6%B2%99%E6%BC%A0%E6%A2%A6%E6%83%B3"
        },
        {
            index: Int32("12"),
            title: "赖清德言论遭全台教师怒轰",
            hot: "829.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%B5%96%E6%B8%85%E5%BE%B7%E8%A8%80%E8%AE%BA%E9%81%AD%E5%85%A8%E5%8F%B0%E6%95%99%E5%B8%88%E6%80%92%E8%BD%B0"
        },
        {
            index: Int32("13"),
            title: "“没签劳动合同就没劳动关系”不实",
            hot: "812.2万",
            label: "16",
            url: "https://www.douyin.com/search/%E2%80%9C%E6%B2%A1%E7%AD%BE%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E5%B0%B1%E6%B2%A1%E5%8A%B3%E5%8A%A8%E5%85%B3%E7%B3%BB%E2%80%9D%E4%B8%8D%E5%AE%9E"
        },
        {
            index: Int32("14"),
            title: "海克斯大乱斗新春版本",
            hot: "779万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%85%8B%E6%96%AF%E5%A4%A7%E4%B9%B1%E6%96%97%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC"
        },
        {
            index: Int32("15"),
            title: "记录我的春运返乡故事",
            hot: "778.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E6%98%A5%E8%BF%90%E8%BF%94%E4%B9%A1%E6%95%85%E4%BA%8B"
        },
        {
            index: Int32("16"),
            title: "年夜饭菜单提前曝光了",
            hot: "776.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%A4%9C%E9%A5%AD%E8%8F%9C%E5%8D%95%E6%8F%90%E5%89%8D%E6%9B%9D%E5%85%89%E4%BA%86"
        },
        {
            index: Int32("17"),
            title: "安徽萧县地震",
            hot: "775.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%89%E5%BE%BD%E8%90%A7%E5%8E%BF%E5%9C%B0%E9%9C%87"
        },
        {
            index: Int32("18"),
            title: "灵隐寺将暂停爽约者预约资格",
            hot: "775.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%81%B5%E9%9A%90%E5%AF%BA%E5%B0%86%E6%9A%82%E5%81%9C%E7%88%BD%E7%BA%A6%E8%80%85%E9%A2%84%E7%BA%A6%E8%B5%84%E6%A0%BC"
        },
        {
            index: Int32("19"),
            title: "记录我的一半一半",
            hot: "775.2万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("20"),
            title: "整治农村高额彩礼今年有了新要求",
            hot: "773.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%95%B4%E6%B2%BB%E5%86%9C%E6%9D%91%E9%AB%98%E9%A2%9D%E5%BD%A9%E7%A4%BC%E4%BB%8A%E5%B9%B4%E6%9C%89%E4%BA%86%E6%96%B0%E8%A6%81%E6%B1%82"
        },
        {
            index: Int32("21"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "773.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("22"),
            title: "吕布新皮肤舞狮寰",
            hot: "773万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%90%95%E5%B8%83%E6%96%B0%E7%9A%AE%E8%82%A4%E8%88%9E%E7%8B%AE%E5%AF%B0"
        },
        {
            index: Int32("23"),
            title: "金宣虎承认逃税并道歉",
            hot: "772.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E5%AE%A3%E8%99%8E%E6%89%BF%E8%AE%A4%E9%80%83%E7%A8%8E%E5%B9%B6%E9%81%93%E6%AD%89"
        },
        {
            index: Int32("24"),
            title: "驻美记者解读爱泼斯坦案最新进展",
            hot: "772.7万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%A9%BB%E7%BE%8E%E8%AE%B0%E8%80%85%E8%A7%A3%E8%AF%BB%E7%88%B1%E6%B3%BC%E6%96%AF%E5%9D%A6%E6%A1%88%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95"
        },
        {
            index: Int32("25"),
            title: "王者马年限定皮肤形象首曝",
            hot: "772.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E5%B9%B4%E9%99%90%E5%AE%9A%E7%9A%AE%E8%82%A4%E5%BD%A2%E8%B1%A1%E9%A6%96%E6%9B%9D"
        },
        {
            index: Int32("26"),
            title: "年少有为打工人狠狠共情了",
            hot: "772万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E6%89%93%E5%B7%A5%E4%BA%BA%E7%8B%A0%E7%8B%A0%E5%85%B1%E6%83%85%E4%BA%86"
        },
        {
            index: Int32("27"),
            title: "王楚钦3:0帕尔",
            hot: "771.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E6%A5%9A%E9%92%A63%3A0%E5%B8%95%E5%B0%94"
        },
        {
            index: Int32("28"),
            title: "EDG不敌BLG",
            hot: "771.1万",
            label: "0",
            url: "https://www.douyin.com/search/EDG%E4%B8%8D%E6%95%8CBLG"
        },
        {
            index: Int32("29"),
            title: "守望先锋新英雄爆料",
            hot: "770.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%88%E6%9C%9B%E5%85%88%E9%94%8B%E6%96%B0%E8%8B%B1%E9%9B%84%E7%88%86%E6%96%99"
        },
        {
            index: Int32("30"),
            title: "短剧演员红毯视频完播率100%",
            hot: "770.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("31"),
            title: "惊蛰无声OST阵容官宣",
            hot: "769万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0OST%E9%98%B5%E5%AE%B9%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("32"),
            title: "群星迎春仪式感",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%A4%E6%98%9F%E8%BF%8E%E6%98%A5%E4%BB%AA%E5%BC%8F%E6%84%9F"
        },
        {
            index: Int32("33"),
            title: "陈哲远给我擦皮鞋变装",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%99%88%E5%93%B2%E8%BF%9C%E7%BB%99%E6%88%91%E6%93%A6%E7%9A%AE%E9%9E%8B%E5%8F%98%E8%A3%85"
        },
        {
            index: Int32("34"),
            title: "吃牟平烧烤就要到牟平",
            hot: "768.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%83%E7%89%9F%E5%B9%B3%E7%83%A7%E7%83%A4%E5%B0%B1%E8%A6%81%E5%88%B0%E7%89%9F%E5%B9%B3"
        },
        {
            index: Int32("35"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "767.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("36"),
            title: "杨紫生命树演技获好评",
            hot: "767.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%9D%A8%E7%B4%AB%E7%94%9F%E5%91%BD%E6%A0%91%E6%BC%94%E6%8A%80%E8%8E%B7%E5%A5%BD%E8%AF%84"
        },
        {
            index: Int32("37"),
            title: "2026年NBA全明星球衣发布",
            hot: "767.6万",
            label: "0",
            url: "https://www.douyin.com/search/2026%E5%B9%B4NBA%E5%85%A8%E6%98%8E%E6%98%9F%E7%90%83%E8%A1%A3%E5%8F%91%E5%B8%83"
        },
        {
            index: Int32("38"),
            title: "白鹿新剧办案不要命",
            hot: "767.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%96%B0%E5%89%A7%E5%8A%9E%E6%A1%88%E4%B8%8D%E8%A6%81%E5%91%BD"
        },
        {
            index: Int32("39"),
            title: "苏新皓萌成啥样了",
            hot: "767.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E8%8B%8F%E6%96%B0%E7%9A%93%E8%90%8C%E6%88%90%E5%95%A5%E6%A0%B7%E4%BA%86"
        },
        {
            index: Int32("40"),
            title: "镜头一拉就长大了",
            hot: "767.4万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("41"),
            title: "朱志鑫黑t战神",
            hot: "766.8万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%9C%B1%E5%BF%97%E9%91%AB%E9%BB%91t%E6%88%98%E7%A5%9E"
        },
        {
            index: Int32("42"),
            title: "生命树多杰暴雪绝境救白菊",
            hot: "765.9万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%A4%9A%E6%9D%B0%E6%9A%B4%E9%9B%AA%E7%BB%9D%E5%A2%83%E6%95%91%E7%99%BD%E8%8F%8A"
        },
        {
            index: Int32("43"),
            title: "恋与深空的古风小生来了",
            hot: "765.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E7%9A%84%E5%8F%A4%E9%A3%8E%E5%B0%8F%E7%94%9F%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("44"),
            title: "周翊然包上恩共创班尖子生",
            hot: "765.4万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E5%85%B1%E5%88%9B%E7%8F%AD%E5%B0%96%E5%AD%90%E7%94%9F"
        },
        {
            index: Int32("45"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "765.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("46"),
            title: "听单依纯立春断舍离",
            hot: "764.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("47"),
            title: "辛芷蕾新剧被林雨申要名分",
            hot: "764.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BE%9B%E8%8A%B7%E8%95%BE%E6%96%B0%E5%89%A7%E8%A2%AB%E6%9E%97%E9%9B%A8%E7%94%B3%E8%A6%81%E5%90%8D%E5%88%86"
        },
        {
            index: Int32("48"),
            title: "张泽禹萌商在我之上",
            hot: "764.6万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BC%A0%E6%B3%BD%E7%A6%B9%E8%90%8C%E5%95%86%E5%9C%A8%E6%88%91%E4%B9%8B%E4%B8%8A"
        },
        {
            index: Int32("49"),
            title: "桃黑黑一诺演我打王者",
            hot: "764.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%A1%83%E9%BB%91%E9%BB%91%E4%B8%80%E8%AF%BA%E6%BC%94%E6%88%91%E6%89%93%E7%8E%8B%E8%80%85"
        },
        {
            index: Int32("50"),
            title: "太平年水丘下线忠臣绝后",
            hot: "764.5万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E6%B0%B4%E4%B8%98%E4%B8%8B%E7%BA%BF%E5%BF%A0%E8%87%A3%E7%BB%9D%E5%90%8E"
        },
        {
            index: Int32("51"),
            title: "陈奕恒单人cha",
            hot: "764.2万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%99%88%E5%A5%95%E6%81%92%E5%8D%95%E4%BA%BAcha"
        }
    ],
    createdAt: ISODate("2026-02-05T03:03:14.734Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("698408fd42a2477ceedfa1c9"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "习近平同普京举行视频会晤",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E6%99%AE%E4%BA%AC%E4%B8%BE%E8%A1%8C%E8%A7%86%E9%A2%91%E4%BC%9A%E6%99%A4"
        },
        {
            index: Int32("2"),
            title: "习近平同特朗普通电话",
            hot: "1195.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E7%89%B9%E6%9C%97%E6%99%AE%E9%80%9A%E7%94%B5%E8%AF%9D"
        },
        {
            index: Int32("3"),
            title: "各地春节年俗地图",
            hot: "1136.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("4"),
            title: "农业综合生产能力迈上新台阶",
            hot: "1118万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E7%94%9F%E4%BA%A7%E8%83%BD%E5%8A%9B%E8%BF%88%E4%B8%8A%E6%96%B0%E5%8F%B0%E9%98%B6"
        },
        {
            index: Int32("5"),
            title: "霉豆腐的风还是吹到了蛋糕界",
            hot: "1075.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%9C%89%E8%B1%86%E8%85%90%E7%9A%84%E9%A3%8E%E8%BF%98%E6%98%AF%E5%90%B9%E5%88%B0%E4%BA%86%E8%9B%8B%E7%B3%95%E7%95%8C"
        },
        {
            index: Int32("6"),
            title: "过年氛围提前搞起来了",
            hot: "1020.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("7"),
            title: "粉彩风和立春一起来了",
            hot: "1019.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%B2%89%E5%BD%A9%E9%A3%8E%E5%92%8C%E7%AB%8B%E6%98%A5%E4%B8%80%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("8"),
            title: "浓眉被交易至奇才",
            hot: "911.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "882.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "这才是跨火盆的满分答案",
            hot: "864.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%99%E6%89%8D%E6%98%AF%E8%B7%A8%E7%81%AB%E7%9B%86%E7%9A%84%E6%BB%A1%E5%88%86%E7%AD%94%E6%A1%88"
        },
        {
            index: Int32("11"),
            title: "一个28岁青年的沙漠梦想",
            hot: "841.6万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%B8%AA28%E5%B2%81%E9%9D%92%E5%B9%B4%E7%9A%84%E6%B2%99%E6%BC%A0%E6%A2%A6%E6%83%B3"
        },
        {
            index: Int32("12"),
            title: "赖清德言论遭全台教师怒轰",
            hot: "829.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%B5%96%E6%B8%85%E5%BE%B7%E8%A8%80%E8%AE%BA%E9%81%AD%E5%85%A8%E5%8F%B0%E6%95%99%E5%B8%88%E6%80%92%E8%BD%B0"
        },
        {
            index: Int32("13"),
            title: "“没签劳动合同就没劳动关系”不实",
            hot: "812.2万",
            label: "16",
            url: "https://www.douyin.com/search/%E2%80%9C%E6%B2%A1%E7%AD%BE%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E5%B0%B1%E6%B2%A1%E5%8A%B3%E5%8A%A8%E5%85%B3%E7%B3%BB%E2%80%9D%E4%B8%8D%E5%AE%9E"
        },
        {
            index: Int32("14"),
            title: "海克斯大乱斗新春版本",
            hot: "779万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%85%8B%E6%96%AF%E5%A4%A7%E4%B9%B1%E6%96%97%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC"
        },
        {
            index: Int32("15"),
            title: "记录我的春运返乡故事",
            hot: "778.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E6%98%A5%E8%BF%90%E8%BF%94%E4%B9%A1%E6%95%85%E4%BA%8B"
        },
        {
            index: Int32("16"),
            title: "年夜饭菜单提前曝光了",
            hot: "776.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%A4%9C%E9%A5%AD%E8%8F%9C%E5%8D%95%E6%8F%90%E5%89%8D%E6%9B%9D%E5%85%89%E4%BA%86"
        },
        {
            index: Int32("17"),
            title: "安徽萧县地震",
            hot: "775.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%89%E5%BE%BD%E8%90%A7%E5%8E%BF%E5%9C%B0%E9%9C%87"
        },
        {
            index: Int32("18"),
            title: "灵隐寺将暂停爽约者预约资格",
            hot: "775.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%81%B5%E9%9A%90%E5%AF%BA%E5%B0%86%E6%9A%82%E5%81%9C%E7%88%BD%E7%BA%A6%E8%80%85%E9%A2%84%E7%BA%A6%E8%B5%84%E6%A0%BC"
        },
        {
            index: Int32("19"),
            title: "记录我的一半一半",
            hot: "775.2万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("20"),
            title: "整治农村高额彩礼今年有了新要求",
            hot: "773.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%95%B4%E6%B2%BB%E5%86%9C%E6%9D%91%E9%AB%98%E9%A2%9D%E5%BD%A9%E7%A4%BC%E4%BB%8A%E5%B9%B4%E6%9C%89%E4%BA%86%E6%96%B0%E8%A6%81%E6%B1%82"
        },
        {
            index: Int32("21"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "773.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("22"),
            title: "吕布新皮肤舞狮寰",
            hot: "773万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%90%95%E5%B8%83%E6%96%B0%E7%9A%AE%E8%82%A4%E8%88%9E%E7%8B%AE%E5%AF%B0"
        },
        {
            index: Int32("23"),
            title: "金宣虎承认逃税并道歉",
            hot: "772.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E5%AE%A3%E8%99%8E%E6%89%BF%E8%AE%A4%E9%80%83%E7%A8%8E%E5%B9%B6%E9%81%93%E6%AD%89"
        },
        {
            index: Int32("24"),
            title: "驻美记者解读爱泼斯坦案最新进展",
            hot: "772.7万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%A9%BB%E7%BE%8E%E8%AE%B0%E8%80%85%E8%A7%A3%E8%AF%BB%E7%88%B1%E6%B3%BC%E6%96%AF%E5%9D%A6%E6%A1%88%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95"
        },
        {
            index: Int32("25"),
            title: "王者马年限定皮肤形象首曝",
            hot: "772.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E5%B9%B4%E9%99%90%E5%AE%9A%E7%9A%AE%E8%82%A4%E5%BD%A2%E8%B1%A1%E9%A6%96%E6%9B%9D"
        },
        {
            index: Int32("26"),
            title: "年少有为打工人狠狠共情了",
            hot: "772万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E6%89%93%E5%B7%A5%E4%BA%BA%E7%8B%A0%E7%8B%A0%E5%85%B1%E6%83%85%E4%BA%86"
        },
        {
            index: Int32("27"),
            title: "王楚钦3:0帕尔",
            hot: "771.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E6%A5%9A%E9%92%A63%3A0%E5%B8%95%E5%B0%94"
        },
        {
            index: Int32("28"),
            title: "EDG不敌BLG",
            hot: "771.1万",
            label: "0",
            url: "https://www.douyin.com/search/EDG%E4%B8%8D%E6%95%8CBLG"
        },
        {
            index: Int32("29"),
            title: "守望先锋新英雄爆料",
            hot: "770.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%88%E6%9C%9B%E5%85%88%E9%94%8B%E6%96%B0%E8%8B%B1%E9%9B%84%E7%88%86%E6%96%99"
        },
        {
            index: Int32("30"),
            title: "短剧演员红毯视频完播率100%",
            hot: "770.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("31"),
            title: "惊蛰无声OST阵容官宣",
            hot: "769万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0OST%E9%98%B5%E5%AE%B9%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("32"),
            title: "群星迎春仪式感",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%A4%E6%98%9F%E8%BF%8E%E6%98%A5%E4%BB%AA%E5%BC%8F%E6%84%9F"
        },
        {
            index: Int32("33"),
            title: "陈哲远给我擦皮鞋变装",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%99%88%E5%93%B2%E8%BF%9C%E7%BB%99%E6%88%91%E6%93%A6%E7%9A%AE%E9%9E%8B%E5%8F%98%E8%A3%85"
        },
        {
            index: Int32("34"),
            title: "吃牟平烧烤就要到牟平",
            hot: "768.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%83%E7%89%9F%E5%B9%B3%E7%83%A7%E7%83%A4%E5%B0%B1%E8%A6%81%E5%88%B0%E7%89%9F%E5%B9%B3"
        },
        {
            index: Int32("35"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "767.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("36"),
            title: "杨紫生命树演技获好评",
            hot: "767.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%9D%A8%E7%B4%AB%E7%94%9F%E5%91%BD%E6%A0%91%E6%BC%94%E6%8A%80%E8%8E%B7%E5%A5%BD%E8%AF%84"
        },
        {
            index: Int32("37"),
            title: "2026年NBA全明星球衣发布",
            hot: "767.6万",
            label: "0",
            url: "https://www.douyin.com/search/2026%E5%B9%B4NBA%E5%85%A8%E6%98%8E%E6%98%9F%E7%90%83%E8%A1%A3%E5%8F%91%E5%B8%83"
        },
        {
            index: Int32("38"),
            title: "白鹿新剧办案不要命",
            hot: "767.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%96%B0%E5%89%A7%E5%8A%9E%E6%A1%88%E4%B8%8D%E8%A6%81%E5%91%BD"
        },
        {
            index: Int32("39"),
            title: "苏新皓萌成啥样了",
            hot: "767.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E8%8B%8F%E6%96%B0%E7%9A%93%E8%90%8C%E6%88%90%E5%95%A5%E6%A0%B7%E4%BA%86"
        },
        {
            index: Int32("40"),
            title: "镜头一拉就长大了",
            hot: "767.4万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("41"),
            title: "朱志鑫黑t战神",
            hot: "766.8万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%9C%B1%E5%BF%97%E9%91%AB%E9%BB%91t%E6%88%98%E7%A5%9E"
        },
        {
            index: Int32("42"),
            title: "生命树多杰暴雪绝境救白菊",
            hot: "765.9万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%A4%9A%E6%9D%B0%E6%9A%B4%E9%9B%AA%E7%BB%9D%E5%A2%83%E6%95%91%E7%99%BD%E8%8F%8A"
        },
        {
            index: Int32("43"),
            title: "恋与深空的古风小生来了",
            hot: "765.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E7%9A%84%E5%8F%A4%E9%A3%8E%E5%B0%8F%E7%94%9F%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("44"),
            title: "周翊然包上恩共创班尖子生",
            hot: "765.4万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E5%85%B1%E5%88%9B%E7%8F%AD%E5%B0%96%E5%AD%90%E7%94%9F"
        },
        {
            index: Int32("45"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "765.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("46"),
            title: "听单依纯立春断舍离",
            hot: "764.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("47"),
            title: "辛芷蕾新剧被林雨申要名分",
            hot: "764.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BE%9B%E8%8A%B7%E8%95%BE%E6%96%B0%E5%89%A7%E8%A2%AB%E6%9E%97%E9%9B%A8%E7%94%B3%E8%A6%81%E5%90%8D%E5%88%86"
        },
        {
            index: Int32("48"),
            title: "张泽禹萌商在我之上",
            hot: "764.6万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BC%A0%E6%B3%BD%E7%A6%B9%E8%90%8C%E5%95%86%E5%9C%A8%E6%88%91%E4%B9%8B%E4%B8%8A"
        },
        {
            index: Int32("49"),
            title: "桃黑黑一诺演我打王者",
            hot: "764.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%A1%83%E9%BB%91%E9%BB%91%E4%B8%80%E8%AF%BA%E6%BC%94%E6%88%91%E6%89%93%E7%8E%8B%E8%80%85"
        },
        {
            index: Int32("50"),
            title: "太平年水丘下线忠臣绝后",
            hot: "764.5万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E6%B0%B4%E4%B8%98%E4%B8%8B%E7%BA%BF%E5%BF%A0%E8%87%A3%E7%BB%9D%E5%90%8E"
        },
        {
            index: Int32("51"),
            title: "陈奕恒单人cha",
            hot: "764.2万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%99%88%E5%A5%95%E6%81%92%E5%8D%95%E4%BA%BAcha"
        }
    ],
    createdAt: ISODate("2026-02-05T03:05:33.012Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("6984090542a2477ceedfa1ca"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "习近平同普京举行视频会晤",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E6%99%AE%E4%BA%AC%E4%B8%BE%E8%A1%8C%E8%A7%86%E9%A2%91%E4%BC%9A%E6%99%A4"
        },
        {
            index: Int32("2"),
            title: "习近平同特朗普通电话",
            hot: "1195.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E7%89%B9%E6%9C%97%E6%99%AE%E9%80%9A%E7%94%B5%E8%AF%9D"
        },
        {
            index: Int32("3"),
            title: "各地春节年俗地图",
            hot: "1136.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("4"),
            title: "农业综合生产能力迈上新台阶",
            hot: "1118万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E7%94%9F%E4%BA%A7%E8%83%BD%E5%8A%9B%E8%BF%88%E4%B8%8A%E6%96%B0%E5%8F%B0%E9%98%B6"
        },
        {
            index: Int32("5"),
            title: "霉豆腐的风还是吹到了蛋糕界",
            hot: "1075.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%9C%89%E8%B1%86%E8%85%90%E7%9A%84%E9%A3%8E%E8%BF%98%E6%98%AF%E5%90%B9%E5%88%B0%E4%BA%86%E8%9B%8B%E7%B3%95%E7%95%8C"
        },
        {
            index: Int32("6"),
            title: "过年氛围提前搞起来了",
            hot: "1020.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("7"),
            title: "粉彩风和立春一起来了",
            hot: "1019.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%B2%89%E5%BD%A9%E9%A3%8E%E5%92%8C%E7%AB%8B%E6%98%A5%E4%B8%80%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("8"),
            title: "浓眉被交易至奇才",
            hot: "911.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "882.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "这才是跨火盆的满分答案",
            hot: "864.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%99%E6%89%8D%E6%98%AF%E8%B7%A8%E7%81%AB%E7%9B%86%E7%9A%84%E6%BB%A1%E5%88%86%E7%AD%94%E6%A1%88"
        },
        {
            index: Int32("11"),
            title: "一个28岁青年的沙漠梦想",
            hot: "841.6万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%B8%AA28%E5%B2%81%E9%9D%92%E5%B9%B4%E7%9A%84%E6%B2%99%E6%BC%A0%E6%A2%A6%E6%83%B3"
        },
        {
            index: Int32("12"),
            title: "赖清德言论遭全台教师怒轰",
            hot: "829.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%B5%96%E6%B8%85%E5%BE%B7%E8%A8%80%E8%AE%BA%E9%81%AD%E5%85%A8%E5%8F%B0%E6%95%99%E5%B8%88%E6%80%92%E8%BD%B0"
        },
        {
            index: Int32("13"),
            title: "“没签劳动合同就没劳动关系”不实",
            hot: "812.2万",
            label: "16",
            url: "https://www.douyin.com/search/%E2%80%9C%E6%B2%A1%E7%AD%BE%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E5%B0%B1%E6%B2%A1%E5%8A%B3%E5%8A%A8%E5%85%B3%E7%B3%BB%E2%80%9D%E4%B8%8D%E5%AE%9E"
        },
        {
            index: Int32("14"),
            title: "海克斯大乱斗新春版本",
            hot: "779万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%85%8B%E6%96%AF%E5%A4%A7%E4%B9%B1%E6%96%97%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC"
        },
        {
            index: Int32("15"),
            title: "记录我的春运返乡故事",
            hot: "778.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E6%98%A5%E8%BF%90%E8%BF%94%E4%B9%A1%E6%95%85%E4%BA%8B"
        },
        {
            index: Int32("16"),
            title: "年夜饭菜单提前曝光了",
            hot: "776.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%A4%9C%E9%A5%AD%E8%8F%9C%E5%8D%95%E6%8F%90%E5%89%8D%E6%9B%9D%E5%85%89%E4%BA%86"
        },
        {
            index: Int32("17"),
            title: "安徽萧县地震",
            hot: "775.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%89%E5%BE%BD%E8%90%A7%E5%8E%BF%E5%9C%B0%E9%9C%87"
        },
        {
            index: Int32("18"),
            title: "灵隐寺将暂停爽约者预约资格",
            hot: "775.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%81%B5%E9%9A%90%E5%AF%BA%E5%B0%86%E6%9A%82%E5%81%9C%E7%88%BD%E7%BA%A6%E8%80%85%E9%A2%84%E7%BA%A6%E8%B5%84%E6%A0%BC"
        },
        {
            index: Int32("19"),
            title: "记录我的一半一半",
            hot: "775.2万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("20"),
            title: "整治农村高额彩礼今年有了新要求",
            hot: "773.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%95%B4%E6%B2%BB%E5%86%9C%E6%9D%91%E9%AB%98%E9%A2%9D%E5%BD%A9%E7%A4%BC%E4%BB%8A%E5%B9%B4%E6%9C%89%E4%BA%86%E6%96%B0%E8%A6%81%E6%B1%82"
        },
        {
            index: Int32("21"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "773.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("22"),
            title: "吕布新皮肤舞狮寰",
            hot: "773万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%90%95%E5%B8%83%E6%96%B0%E7%9A%AE%E8%82%A4%E8%88%9E%E7%8B%AE%E5%AF%B0"
        },
        {
            index: Int32("23"),
            title: "金宣虎承认逃税并道歉",
            hot: "772.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E5%AE%A3%E8%99%8E%E6%89%BF%E8%AE%A4%E9%80%83%E7%A8%8E%E5%B9%B6%E9%81%93%E6%AD%89"
        },
        {
            index: Int32("24"),
            title: "驻美记者解读爱泼斯坦案最新进展",
            hot: "772.7万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%A9%BB%E7%BE%8E%E8%AE%B0%E8%80%85%E8%A7%A3%E8%AF%BB%E7%88%B1%E6%B3%BC%E6%96%AF%E5%9D%A6%E6%A1%88%E6%9C%80%E6%96%B0%E8%BF%9B%E5%B1%95"
        },
        {
            index: Int32("25"),
            title: "王者马年限定皮肤形象首曝",
            hot: "772.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E5%B9%B4%E9%99%90%E5%AE%9A%E7%9A%AE%E8%82%A4%E5%BD%A2%E8%B1%A1%E9%A6%96%E6%9B%9D"
        },
        {
            index: Int32("26"),
            title: "年少有为打工人狠狠共情了",
            hot: "772万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E6%89%93%E5%B7%A5%E4%BA%BA%E7%8B%A0%E7%8B%A0%E5%85%B1%E6%83%85%E4%BA%86"
        },
        {
            index: Int32("27"),
            title: "王楚钦3:0帕尔",
            hot: "771.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E6%A5%9A%E9%92%A63%3A0%E5%B8%95%E5%B0%94"
        },
        {
            index: Int32("28"),
            title: "EDG不敌BLG",
            hot: "771.1万",
            label: "0",
            url: "https://www.douyin.com/search/EDG%E4%B8%8D%E6%95%8CBLG"
        },
        {
            index: Int32("29"),
            title: "守望先锋新英雄爆料",
            hot: "770.9万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%AE%88%E6%9C%9B%E5%85%88%E9%94%8B%E6%96%B0%E8%8B%B1%E9%9B%84%E7%88%86%E6%96%99"
        },
        {
            index: Int32("30"),
            title: "短剧演员红毯视频完播率100%",
            hot: "770.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("31"),
            title: "惊蛰无声OST阵容官宣",
            hot: "769万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0OST%E9%98%B5%E5%AE%B9%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("32"),
            title: "群星迎春仪式感",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%A4%E6%98%9F%E8%BF%8E%E6%98%A5%E4%BB%AA%E5%BC%8F%E6%84%9F"
        },
        {
            index: Int32("33"),
            title: "陈哲远给我擦皮鞋变装",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%99%88%E5%93%B2%E8%BF%9C%E7%BB%99%E6%88%91%E6%93%A6%E7%9A%AE%E9%9E%8B%E5%8F%98%E8%A3%85"
        },
        {
            index: Int32("34"),
            title: "吃牟平烧烤就要到牟平",
            hot: "768.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%83%E7%89%9F%E5%B9%B3%E7%83%A7%E7%83%A4%E5%B0%B1%E8%A6%81%E5%88%B0%E7%89%9F%E5%B9%B3"
        },
        {
            index: Int32("35"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "767.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("36"),
            title: "杨紫生命树演技获好评",
            hot: "767.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%9D%A8%E7%B4%AB%E7%94%9F%E5%91%BD%E6%A0%91%E6%BC%94%E6%8A%80%E8%8E%B7%E5%A5%BD%E8%AF%84"
        },
        {
            index: Int32("37"),
            title: "2026年NBA全明星球衣发布",
            hot: "767.6万",
            label: "0",
            url: "https://www.douyin.com/search/2026%E5%B9%B4NBA%E5%85%A8%E6%98%8E%E6%98%9F%E7%90%83%E8%A1%A3%E5%8F%91%E5%B8%83"
        },
        {
            index: Int32("38"),
            title: "白鹿新剧办案不要命",
            hot: "767.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%96%B0%E5%89%A7%E5%8A%9E%E6%A1%88%E4%B8%8D%E8%A6%81%E5%91%BD"
        },
        {
            index: Int32("39"),
            title: "苏新皓萌成啥样了",
            hot: "767.5万",
            label: "17",
            url: "https://www.douyin.com/search/%E8%8B%8F%E6%96%B0%E7%9A%93%E8%90%8C%E6%88%90%E5%95%A5%E6%A0%B7%E4%BA%86"
        },
        {
            index: Int32("40"),
            title: "镜头一拉就长大了",
            hot: "767.4万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("41"),
            title: "朱志鑫黑t战神",
            hot: "766.8万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%9C%B1%E5%BF%97%E9%91%AB%E9%BB%91t%E6%88%98%E7%A5%9E"
        },
        {
            index: Int32("42"),
            title: "生命树多杰暴雪绝境救白菊",
            hot: "765.9万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%A4%9A%E6%9D%B0%E6%9A%B4%E9%9B%AA%E7%BB%9D%E5%A2%83%E6%95%91%E7%99%BD%E8%8F%8A"
        },
        {
            index: Int32("43"),
            title: "恋与深空的古风小生来了",
            hot: "765.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E7%9A%84%E5%8F%A4%E9%A3%8E%E5%B0%8F%E7%94%9F%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("44"),
            title: "周翊然包上恩共创班尖子生",
            hot: "765.4万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E5%85%B1%E5%88%9B%E7%8F%AD%E5%B0%96%E5%AD%90%E7%94%9F"
        },
        {
            index: Int32("45"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "765.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("46"),
            title: "听单依纯立春断舍离",
            hot: "764.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("47"),
            title: "辛芷蕾新剧被林雨申要名分",
            hot: "764.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BE%9B%E8%8A%B7%E8%95%BE%E6%96%B0%E5%89%A7%E8%A2%AB%E6%9E%97%E9%9B%A8%E7%94%B3%E8%A6%81%E5%90%8D%E5%88%86"
        },
        {
            index: Int32("48"),
            title: "张泽禹萌商在我之上",
            hot: "764.6万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BC%A0%E6%B3%BD%E7%A6%B9%E8%90%8C%E5%95%86%E5%9C%A8%E6%88%91%E4%B9%8B%E4%B8%8A"
        },
        {
            index: Int32("49"),
            title: "桃黑黑一诺演我打王者",
            hot: "764.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%A1%83%E9%BB%91%E9%BB%91%E4%B8%80%E8%AF%BA%E6%BC%94%E6%88%91%E6%89%93%E7%8E%8B%E8%80%85"
        },
        {
            index: Int32("50"),
            title: "太平年水丘下线忠臣绝后",
            hot: "764.5万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E6%B0%B4%E4%B8%98%E4%B8%8B%E7%BA%BF%E5%BF%A0%E8%87%A3%E7%BB%9D%E5%90%8E"
        },
        {
            index: Int32("51"),
            title: "陈奕恒单人cha",
            hot: "764.2万",
            label: "17",
            url: "https://www.douyin.com/search/%E9%99%88%E5%A5%95%E6%81%92%E5%8D%95%E4%BA%BAcha"
        }
    ],
    createdAt: ISODate("2026-02-05T03:05:41.381Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("69840b2f01b02c3f864e9534"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "习近平同普京举行视频会晤",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E6%99%AE%E4%BA%AC%E4%B8%BE%E8%A1%8C%E8%A7%86%E9%A2%91%E4%BC%9A%E6%99%A4"
        },
        {
            index: Int32("2"),
            title: "习近平同特朗普通电话",
            hot: "1190.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E7%89%B9%E6%9C%97%E6%99%AE%E9%80%9A%E7%94%B5%E8%AF%9D"
        },
        {
            index: Int32("3"),
            title: "各地春节年俗地图",
            hot: "1134万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("4"),
            title: "农业综合生产能力迈上新台阶",
            hot: "1115.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E7%94%9F%E4%BA%A7%E8%83%BD%E5%8A%9B%E8%BF%88%E4%B8%8A%E6%96%B0%E5%8F%B0%E9%98%B6"
        },
        {
            index: Int32("5"),
            title: "霉豆腐的风还是吹到了蛋糕界",
            hot: "1115万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%9C%89%E8%B1%86%E8%85%90%E7%9A%84%E9%A3%8E%E8%BF%98%E6%98%AF%E5%90%B9%E5%88%B0%E4%BA%86%E8%9B%8B%E7%B3%95%E7%95%8C"
        },
        {
            index: Int32("6"),
            title: "过年氛围提前搞起来了",
            hot: "1018.8万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("7"),
            title: "这才是跨火盆的满分答案",
            hot: "1014万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BF%99%E6%89%8D%E6%98%AF%E8%B7%A8%E7%81%AB%E7%9B%86%E7%9A%84%E6%BB%A1%E5%88%86%E7%AD%94%E6%A1%88"
        },
        {
            index: Int32("8"),
            title: "浓眉被交易至奇才",
            hot: "902.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "871.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "记录我的春运返乡故事",
            hot: "859.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E6%98%A5%E8%BF%90%E8%BF%94%E4%B9%A1%E6%95%85%E4%BA%8B"
        },
        {
            index: Int32("11"),
            title: "一个28岁青年的沙漠梦想",
            hot: "842.2万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%B8%AA28%E5%B2%81%E9%9D%92%E5%B9%B4%E7%9A%84%E6%B2%99%E6%BC%A0%E6%A2%A6%E6%83%B3"
        },
        {
            index: Int32("12"),
            title: "赖清德言论遭全台教师怒轰",
            hot: "806万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%B5%96%E6%B8%85%E5%BE%B7%E8%A8%80%E8%AE%BA%E9%81%AD%E5%85%A8%E5%8F%B0%E6%95%99%E5%B8%88%E6%80%92%E8%BD%B0"
        },
        {
            index: Int32("13"),
            title: "“没签劳动合同就没劳动关系”不实",
            hot: "801.3万",
            label: "16",
            url: "https://www.douyin.com/search/%E2%80%9C%E6%B2%A1%E7%AD%BE%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E5%B0%B1%E6%B2%A1%E5%8A%B3%E5%8A%A8%E5%85%B3%E7%B3%BB%E2%80%9D%E4%B8%8D%E5%AE%9E"
        },
        {
            index: Int32("14"),
            title: "海克斯大乱斗新春版本",
            hot: "786.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%85%8B%E6%96%AF%E5%A4%A7%E4%B9%B1%E6%96%97%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC"
        },
        {
            index: Int32("15"),
            title: "年夜饭菜单提前曝光了",
            hot: "778.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%A4%9C%E9%A5%AD%E8%8F%9C%E5%8D%95%E6%8F%90%E5%89%8D%E6%9B%9D%E5%85%89%E4%BA%86"
        },
        {
            index: Int32("16"),
            title: "王楚钦3:0帕尔",
            hot: "778.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E6%A5%9A%E9%92%A63%3A0%E5%B8%95%E5%B0%94"
        },
        {
            index: Int32("17"),
            title: "安徽萧县地震",
            hot: "775.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AE%89%E5%BE%BD%E8%90%A7%E5%8E%BF%E5%9C%B0%E9%9C%87"
        },
        {
            index: Int32("18"),
            title: "整治农村高额彩礼今年有了新要求",
            hot: "775万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%95%B4%E6%B2%BB%E5%86%9C%E6%9D%91%E9%AB%98%E9%A2%9D%E5%BD%A9%E7%A4%BC%E4%BB%8A%E5%B9%B4%E6%9C%89%E4%BA%86%E6%96%B0%E8%A6%81%E6%B1%82"
        },
        {
            index: Int32("19"),
            title: "2026年苏超赛程正式公布",
            hot: "774.9万",
            label: "3",
            url: "https://www.douyin.com/search/2026%E5%B9%B4%E8%8B%8F%E8%B6%85%E8%B5%9B%E7%A8%8B%E6%AD%A3%E5%BC%8F%E5%85%AC%E5%B8%83"
        },
        {
            index: Int32("20"),
            title: "记录我的一半一半",
            hot: "774.7万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("21"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "773.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("22"),
            title: "金宣虎承认逃税并道歉",
            hot: "773.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E5%AE%A3%E8%99%8E%E6%89%BF%E8%AE%A4%E9%80%83%E7%A8%8E%E5%B9%B6%E9%81%93%E6%AD%89"
        },
        {
            index: Int32("23"),
            title: "年少有为打工人狠狠共情了",
            hot: "772.8万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E6%89%93%E5%B7%A5%E4%BA%BA%E7%8B%A0%E7%8B%A0%E5%85%B1%E6%83%85%E4%BA%86"
        },
        {
            index: Int32("24"),
            title: "被冬奥会中国代表团队服种草了",
            hot: "772.8万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%A2%AB%E5%86%AC%E5%A5%A5%E4%BC%9A%E4%B8%AD%E5%9B%BD%E4%BB%A3%E8%A1%A8%E5%9B%A2%E9%98%9F%E6%9C%8D%E7%A7%8D%E8%8D%89%E4%BA%86"
        },
        {
            index: Int32("25"),
            title: "守望先锋新英雄爆料",
            hot: "772.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AE%88%E6%9C%9B%E5%85%88%E9%94%8B%E6%96%B0%E8%8B%B1%E9%9B%84%E7%88%86%E6%96%99"
        },
        {
            index: Int32("26"),
            title: "吕布新皮肤舞狮寰",
            hot: "772.4万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%90%95%E5%B8%83%E6%96%B0%E7%9A%AE%E8%82%A4%E8%88%9E%E7%8B%AE%E5%AF%B0"
        },
        {
            index: Int32("27"),
            title: "王者马年限定皮肤形象首曝",
            hot: "771.6万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E5%B9%B4%E9%99%90%E5%AE%9A%E7%9A%AE%E8%82%A4%E5%BD%A2%E8%B1%A1%E9%A6%96%E6%9B%9D"
        },
        {
            index: Int32("28"),
            title: "EDG不敌BLG",
            hot: "770.1万",
            label: "0",
            url: "https://www.douyin.com/search/EDG%E4%B8%8D%E6%95%8CBLG"
        },
        {
            index: Int32("29"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "769.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("30"),
            title: "陈哲远给我擦皮鞋变装",
            hot: "769.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%99%88%E5%93%B2%E8%BF%9C%E7%BB%99%E6%88%91%E6%93%A6%E7%9A%AE%E9%9E%8B%E5%8F%98%E8%A3%85"
        },
        {
            index: Int32("31"),
            title: "惊蛰无声OST阵容官宣",
            hot: "769.1万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0OST%E9%98%B5%E5%AE%B9%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("32"),
            title: "群星迎春仪式感",
            hot: "768.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%A4%E6%98%9F%E8%BF%8E%E6%98%A5%E4%BB%AA%E5%BC%8F%E6%84%9F"
        },
        {
            index: Int32("33"),
            title: "吃牟平烧烤就要到牟平",
            hot: "768.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%83%E7%89%9F%E5%B9%B3%E7%83%A7%E7%83%A4%E5%B0%B1%E8%A6%81%E5%88%B0%E7%89%9F%E5%B9%B3"
        },
        {
            index: Int32("34"),
            title: "短剧演员红毯视频完播率100%",
            hot: "768.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("35"),
            title: "杨紫生命树演技获好评",
            hot: "768.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%9D%A8%E7%B4%AB%E7%94%9F%E5%91%BD%E6%A0%91%E6%BC%94%E6%8A%80%E8%8E%B7%E5%A5%BD%E8%AF%84"
        },
        {
            index: Int32("36"),
            title: "2026年NBA全明星球衣发布",
            hot: "768.2万",
            label: "0",
            url: "https://www.douyin.com/search/2026%E5%B9%B4NBA%E5%85%A8%E6%98%8E%E6%98%9F%E7%90%83%E8%A1%A3%E5%8F%91%E5%B8%83"
        },
        {
            index: Int32("37"),
            title: "白鹿新剧办案不要命",
            hot: "768.1万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%96%B0%E5%89%A7%E5%8A%9E%E6%A1%88%E4%B8%8D%E8%A6%81%E5%91%BD"
        },
        {
            index: Int32("38"),
            title: "恋与深空的古风小生来了",
            hot: "767.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E7%9A%84%E5%8F%A4%E9%A3%8E%E5%B0%8F%E7%94%9F%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("39"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "767.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("40"),
            title: "苏新皓萌成啥样了",
            hot: "766.8万",
            label: "17",
            url: "https://www.douyin.com/search/%E8%8B%8F%E6%96%B0%E7%9A%93%E8%90%8C%E6%88%90%E5%95%A5%E6%A0%B7%E4%BA%86"
        },
        {
            index: Int32("41"),
            title: "朱志鑫黑t战神",
            hot: "766.3万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%9C%B1%E5%BF%97%E9%91%AB%E9%BB%91t%E6%88%98%E7%A5%9E"
        },
        {
            index: Int32("42"),
            title: "周翊然包上恩共创班尖子生",
            hot: "766.1万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E5%85%B1%E5%88%9B%E7%8F%AD%E5%B0%96%E5%AD%90%E7%94%9F"
        },
        {
            index: Int32("43"),
            title: "辛芷蕾新剧被林雨申要名分",
            hot: "766万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BE%9B%E8%8A%B7%E8%95%BE%E6%96%B0%E5%89%A7%E8%A2%AB%E6%9E%97%E9%9B%A8%E7%94%B3%E8%A6%81%E5%90%8D%E5%88%86"
        },
        {
            index: Int32("44"),
            title: "生命树多杰暴雪绝境救白菊",
            hot: "765.5万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%A4%9A%E6%9D%B0%E6%9A%B4%E9%9B%AA%E7%BB%9D%E5%A2%83%E6%95%91%E7%99%BD%E8%8F%8A"
        },
        {
            index: Int32("45"),
            title: "镜头一拉就长大了",
            hot: "765.3万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("46"),
            title: "张泽禹萌商在我之上",
            hot: "765.1万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BC%A0%E6%B3%BD%E7%A6%B9%E8%90%8C%E5%95%86%E5%9C%A8%E6%88%91%E4%B9%8B%E4%B8%8A"
        },
        {
            index: Int32("47"),
            title: "丁程鑫也来挑战泼水成冰了",
            hot: "764.9万",
            label: "17",
            url: "https://www.douyin.com/search/%E4%B8%81%E7%A8%8B%E9%91%AB%E4%B9%9F%E6%9D%A5%E6%8C%91%E6%88%98%E6%B3%BC%E6%B0%B4%E6%88%90%E5%86%B0%E4%BA%86"
        },
        {
            index: Int32("48"),
            title: "听单依纯立春断舍离",
            hot: "764.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("49"),
            title: "桃黑黑一诺演我打王者",
            hot: "764.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%A1%83%E9%BB%91%E9%BB%91%E4%B8%80%E8%AF%BA%E6%BC%94%E6%88%91%E6%89%93%E7%8E%8B%E8%80%85"
        },
        {
            index: Int32("50"),
            title: "太平年水丘下线忠臣绝后",
            hot: "764.6万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E6%B0%B4%E4%B8%98%E4%B8%8B%E7%BA%BF%E5%BF%A0%E8%87%A3%E7%BB%9D%E5%90%8E"
        },
        {
            index: Int32("51"),
            title: "崔秀彬跳支弥渡山歌给MOA看",
            hot: "764.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%B4%94%E7%A7%80%E5%BD%AC%E8%B7%B3%E6%94%AF%E5%BC%A5%E6%B8%A1%E5%B1%B1%E6%AD%8C%E7%BB%99MOA%E7%9C%8B"
        }
    ],
    createdAt: ISODate("2026-02-05T03:14:55.389Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("69840ba8376d75031b643fab"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "习近平同普京举行视频会晤",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E6%99%AE%E4%BA%AC%E4%B8%BE%E8%A1%8C%E8%A7%86%E9%A2%91%E4%BC%9A%E6%99%A4"
        },
        {
            index: Int32("2"),
            title: "习近平同特朗普通电话",
            hot: "1186.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B9%A0%E8%BF%91%E5%B9%B3%E5%90%8C%E7%89%B9%E6%9C%97%E6%99%AE%E9%80%9A%E7%94%B5%E8%AF%9D"
        },
        {
            index: Int32("3"),
            title: "各地春节年俗地图",
            hot: "1133.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("4"),
            title: "农业综合生产能力迈上新台阶",
            hot: "1117万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%9C%E4%B8%9A%E7%BB%BC%E5%90%88%E7%94%9F%E4%BA%A7%E8%83%BD%E5%8A%9B%E8%BF%88%E4%B8%8A%E6%96%B0%E5%8F%B0%E9%98%B6"
        },
        {
            index: Int32("5"),
            title: "过年氛围提前搞起来了",
            hot: "1115.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("6"),
            title: "霉豆腐的风还是吹到了蛋糕界",
            hot: "1018.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E9%9C%89%E8%B1%86%E8%85%90%E7%9A%84%E9%A3%8E%E8%BF%98%E6%98%AF%E5%90%B9%E5%88%B0%E4%BA%86%E8%9B%8B%E7%B3%95%E7%95%8C"
        },
        {
            index: Int32("7"),
            title: "这才是跨火盆的满分答案",
            hot: "1012.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BF%99%E6%89%8D%E6%98%AF%E8%B7%A8%E7%81%AB%E7%9B%86%E7%9A%84%E6%BB%A1%E5%88%86%E7%AD%94%E6%A1%88"
        },
        {
            index: Int32("8"),
            title: "浓眉被交易至奇才",
            hot: "900.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "869.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "记录我的春运返乡故事",
            hot: "858.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E6%98%A5%E8%BF%90%E8%BF%94%E4%B9%A1%E6%95%85%E4%BA%8B"
        },
        {
            index: Int32("11"),
            title: "一个28岁青年的沙漠梦想",
            hot: "842.4万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%B8%AA28%E5%B2%81%E9%9D%92%E5%B9%B4%E7%9A%84%E6%B2%99%E6%BC%A0%E6%A2%A6%E6%83%B3"
        },
        {
            index: Int32("12"),
            title: "赖清德言论遭全台教师怒轰",
            hot: "806.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%B5%96%E6%B8%85%E5%BE%B7%E8%A8%80%E8%AE%BA%E9%81%AD%E5%85%A8%E5%8F%B0%E6%95%99%E5%B8%88%E6%80%92%E8%BD%B0"
        },
        {
            index: Int32("13"),
            title: "“没签劳动合同就没劳动关系”不实",
            hot: "798.5万",
            label: "16",
            url: "https://www.douyin.com/search/%E2%80%9C%E6%B2%A1%E7%AD%BE%E5%8A%B3%E5%8A%A8%E5%90%88%E5%90%8C%E5%B0%B1%E6%B2%A1%E5%8A%B3%E5%8A%A8%E5%85%B3%E7%B3%BB%E2%80%9D%E4%B8%8D%E5%AE%9E"
        },
        {
            index: Int32("14"),
            title: "海克斯大乱斗新春版本",
            hot: "785万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%85%8B%E6%96%AF%E5%A4%A7%E4%B9%B1%E6%96%97%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC"
        },
        {
            index: Int32("15"),
            title: "年夜饭菜单提前曝光了",
            hot: "778.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%A4%9C%E9%A5%AD%E8%8F%9C%E5%8D%95%E6%8F%90%E5%89%8D%E6%9B%9D%E5%85%89%E4%BA%86"
        },
        {
            index: Int32("16"),
            title: "王楚钦3:0帕尔",
            hot: "778.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E6%A5%9A%E9%92%A63%3A0%E5%B8%95%E5%B0%94"
        },
        {
            index: Int32("17"),
            title: "安徽萧县地震",
            hot: "775.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AE%89%E5%BE%BD%E8%90%A7%E5%8E%BF%E5%9C%B0%E9%9C%87"
        },
        {
            index: Int32("18"),
            title: "整治农村高额彩礼今年有了新要求",
            hot: "775.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%95%B4%E6%B2%BB%E5%86%9C%E6%9D%91%E9%AB%98%E9%A2%9D%E5%BD%A9%E7%A4%BC%E4%BB%8A%E5%B9%B4%E6%9C%89%E4%BA%86%E6%96%B0%E8%A6%81%E6%B1%82"
        },
        {
            index: Int32("19"),
            title: "2026年苏超赛程正式公布",
            hot: "775.1万",
            label: "3",
            url: "https://www.douyin.com/search/2026%E5%B9%B4%E8%8B%8F%E8%B6%85%E8%B5%9B%E7%A8%8B%E6%AD%A3%E5%BC%8F%E5%85%AC%E5%B8%83"
        },
        {
            index: Int32("20"),
            title: "记录我的一半一半",
            hot: "774.9万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("21"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "774万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("22"),
            title: "金宣虎承认逃税并道歉",
            hot: "773.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E5%AE%A3%E8%99%8E%E6%89%BF%E8%AE%A4%E9%80%83%E7%A8%8E%E5%B9%B6%E9%81%93%E6%AD%89"
        },
        {
            index: Int32("23"),
            title: "年少有为打工人狠狠共情了",
            hot: "773.1万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E6%89%93%E5%B7%A5%E4%BA%BA%E7%8B%A0%E7%8B%A0%E5%85%B1%E6%83%85%E4%BA%86"
        },
        {
            index: Int32("24"),
            title: "守望先锋新英雄爆料",
            hot: "772.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AE%88%E6%9C%9B%E5%85%88%E9%94%8B%E6%96%B0%E8%8B%B1%E9%9B%84%E7%88%86%E6%96%99"
        },
        {
            index: Int32("25"),
            title: "吕布新皮肤舞狮寰",
            hot: "772.4万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%90%95%E5%B8%83%E6%96%B0%E7%9A%AE%E8%82%A4%E8%88%9E%E7%8B%AE%E5%AF%B0"
        },
        {
            index: Int32("26"),
            title: "王者马年限定皮肤形象首曝",
            hot: "772.2万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E5%B9%B4%E9%99%90%E5%AE%9A%E7%9A%AE%E8%82%A4%E5%BD%A2%E8%B1%A1%E9%A6%96%E6%9B%9D"
        },
        {
            index: Int32("27"),
            title: "EDG不敌BLG",
            hot: "771.6万",
            label: "0",
            url: "https://www.douyin.com/search/EDG%E4%B8%8D%E6%95%8CBLG"
        },
        {
            index: Int32("28"),
            title: "杨紫生命树演技获好评",
            hot: "770.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%9D%A8%E7%B4%AB%E7%94%9F%E5%91%BD%E6%A0%91%E6%BC%94%E6%8A%80%E8%8E%B7%E5%A5%BD%E8%AF%84"
        },
        {
            index: Int32("29"),
            title: "惊蛰无声OST阵容官宣",
            hot: "769.7万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0OST%E9%98%B5%E5%AE%B9%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("30"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "769.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("31"),
            title: "陈哲远给我擦皮鞋变装",
            hot: "769.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%99%88%E5%93%B2%E8%BF%9C%E7%BB%99%E6%88%91%E6%93%A6%E7%9A%AE%E9%9E%8B%E5%8F%98%E8%A3%85"
        },
        {
            index: Int32("32"),
            title: "群星迎春仪式感",
            hot: "768.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%A4%E6%98%9F%E8%BF%8E%E6%98%A5%E4%BB%AA%E5%BC%8F%E6%84%9F"
        },
        {
            index: Int32("33"),
            title: "吃牟平烧烤就要到牟平",
            hot: "768.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%83%E7%89%9F%E5%B9%B3%E7%83%A7%E7%83%A4%E5%B0%B1%E8%A6%81%E5%88%B0%E7%89%9F%E5%B9%B3"
        },
        {
            index: Int32("34"),
            title: "短剧演员红毯视频完播率100%",
            hot: "768.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("35"),
            title: "白鹿新剧办案不要命",
            hot: "768.3万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%96%B0%E5%89%A7%E5%8A%9E%E6%A1%88%E4%B8%8D%E8%A6%81%E5%91%BD"
        },
        {
            index: Int32("36"),
            title: "恋与深空的古风小生来了",
            hot: "768.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E7%9A%84%E5%8F%A4%E9%A3%8E%E5%B0%8F%E7%94%9F%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("37"),
            title: "周翊然包上恩共创班尖子生",
            hot: "767.7万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%91%A8%E7%BF%8A%E7%84%B6%E5%8C%85%E4%B8%8A%E6%81%A9%E5%85%B1%E5%88%9B%E7%8F%AD%E5%B0%96%E5%AD%90%E7%94%9F"
        },
        {
            index: Int32("38"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "767.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("39"),
            title: "苏新皓萌成啥样了",
            hot: "766.9万",
            label: "17",
            url: "https://www.douyin.com/search/%E8%8B%8F%E6%96%B0%E7%9A%93%E8%90%8C%E6%88%90%E5%95%A5%E6%A0%B7%E4%BA%86"
        },
        {
            index: Int32("40"),
            title: "2026年NBA全明星球衣发布",
            hot: "766.5万",
            label: "0",
            url: "https://www.douyin.com/search/2026%E5%B9%B4NBA%E5%85%A8%E6%98%8E%E6%98%9F%E7%90%83%E8%A1%A3%E5%8F%91%E5%B8%83"
        },
        {
            index: Int32("41"),
            title: "朱志鑫黑t战神",
            hot: "766.1万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%9C%B1%E5%BF%97%E9%91%AB%E9%BB%91t%E6%88%98%E7%A5%9E"
        },
        {
            index: Int32("42"),
            title: "辛芷蕾新剧被林雨申要名分",
            hot: "766万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%BE%9B%E8%8A%B7%E8%95%BE%E6%96%B0%E5%89%A7%E8%A2%AB%E6%9E%97%E9%9B%A8%E7%94%B3%E8%A6%81%E5%90%8D%E5%88%86"
        },
        {
            index: Int32("43"),
            title: "生命树多杰暴雪绝境救白菊",
            hot: "765.5万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%A4%9A%E6%9D%B0%E6%9A%B4%E9%9B%AA%E7%BB%9D%E5%A2%83%E6%95%91%E7%99%BD%E8%8F%8A"
        },
        {
            index: Int32("44"),
            title: "张泽禹萌商在我之上",
            hot: "765.3万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BC%A0%E6%B3%BD%E7%A6%B9%E8%90%8C%E5%95%86%E5%9C%A8%E6%88%91%E4%B9%8B%E4%B8%8A"
        },
        {
            index: Int32("45"),
            title: "听单依纯立春断舍离",
            hot: "765.1万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("46"),
            title: "丁程鑫也来挑战泼水成冰了",
            hot: "765万",
            label: "17",
            url: "https://www.douyin.com/search/%E4%B8%81%E7%A8%8B%E9%91%AB%E4%B9%9F%E6%9D%A5%E6%8C%91%E6%88%98%E6%B3%BC%E6%B0%B4%E6%88%90%E5%86%B0%E4%BA%86"
        },
        {
            index: Int32("47"),
            title: "桃黑黑一诺演我打王者",
            hot: "764.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%A1%83%E9%BB%91%E9%BB%91%E4%B8%80%E8%AF%BA%E6%BC%94%E6%88%91%E6%89%93%E7%8E%8B%E8%80%85"
        },
        {
            index: Int32("48"),
            title: "太平年水丘下线忠臣绝后",
            hot: "764.9万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E6%B0%B4%E4%B8%98%E4%B8%8B%E7%BA%BF%E5%BF%A0%E8%87%A3%E7%BB%9D%E5%90%8E"
        },
        {
            index: Int32("49"),
            title: "镜头一拉就长大了",
            hot: "764.6万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("50"),
            title: "被冬奥会中国代表团队服种草了",
            hot: "764.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%A2%AB%E5%86%AC%E5%A5%A5%E4%BC%9A%E4%B8%AD%E5%9B%BD%E4%BB%A3%E8%A1%A8%E5%9B%A2%E9%98%9F%E6%9C%8D%E7%A7%8D%E8%8D%89%E4%BA%86"
        },
        {
            index: Int32("51"),
            title: "崔秀彬跳支弥渡山歌给MOA看",
            hot: "764.1万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%B4%94%E7%A7%80%E5%BD%AC%E8%B7%B3%E6%94%AF%E5%BC%A5%E6%B8%A1%E5%B1%B1%E6%AD%8C%E7%BB%99MOA%E7%9C%8B"
        }
    ],
    createdAt: ISODate("2026-02-05T03:16:56.868Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("6984718a40d48b60ff2e7129"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "中俄元首老友再相见",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B8%AD%E4%BF%84%E5%85%83%E9%A6%96%E8%80%81%E5%8F%8B%E5%86%8D%E7%9B%B8%E8%A7%81"
        },
        {
            index: Int32("2"),
            title: "立陶宛承认对中国犯了巨大错误",
            hot: "1158.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%AB%8B%E9%99%B6%E5%AE%9B%E6%89%BF%E8%AE%A4%E5%AF%B9%E4%B8%AD%E5%9B%BD%E7%8A%AF%E4%BA%86%E5%B7%A8%E5%A4%A7%E9%94%99%E8%AF%AF"
        },
        {
            index: Int32("3"),
            title: "加6成受访者支持进口中国电车",
            hot: "1141.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%8A%A06%E6%88%90%E5%8F%97%E8%AE%BF%E8%80%85%E6%94%AF%E6%8C%81%E8%BF%9B%E5%8F%A3%E4%B8%AD%E5%9B%BD%E7%94%B5%E8%BD%A6"
        },
        {
            index: Int32("4"),
            title: "我国网民规模达11.25亿人",
            hot: "1133.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%88%91%E5%9B%BD%E7%BD%91%E6%B0%91%E8%A7%84%E6%A8%A1%E8%BE%BE11.25%E4%BA%BF%E4%BA%BA"
        },
        {
            index: Int32("5"),
            title: "彩虹霉豆腐申请出战",
            hot: "1108.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%BD%A9%E8%99%B9%E9%9C%89%E8%B1%86%E8%85%90%E7%94%B3%E8%AF%B7%E5%87%BA%E6%88%98"
        },
        {
            index: Int32("6"),
            title: "过年氛围提前搞起来了",
            hot: "1033万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%87%E5%B9%B4%E6%B0%9B%E5%9B%B4%E6%8F%90%E5%89%8D%E6%90%9E%E8%B5%B7%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("7"),
            title: "小洛熙事件调查结果",
            hot: "1018.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%B0%8F%E6%B4%9B%E7%86%99%E4%BA%8B%E4%BB%B6%E8%B0%83%E6%9F%A5%E7%BB%93%E6%9E%9C"
        },
        {
            index: Int32("8"),
            title: "各地春节年俗地图",
            hot: "896.8万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%90%84%E5%9C%B0%E6%98%A5%E8%8A%82%E5%B9%B4%E4%BF%97%E5%9C%B0%E5%9B%BE"
        },
        {
            index: Int32("9"),
            title: "第一口春味是家乡的年味",
            hot: "894.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%AC%AC%E4%B8%80%E5%8F%A3%E6%98%A5%E5%91%B3%E6%98%AF%E5%AE%B6%E4%B9%A1%E7%9A%84%E5%B9%B4%E5%91%B3"
        },
        {
            index: Int32("10"),
            title: "王者马限貂蝉美出长安盛世",
            hot: "866万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E9%A9%AC%E9%99%90%E8%B2%82%E8%9D%89%E7%BE%8E%E5%87%BA%E9%95%BF%E5%AE%89%E7%9B%9B%E4%B8%96"
        },
        {
            index: Int32("11"),
            title: "和平精英小火人联动",
            hot: "828.5万",
            label: "9",
            url: "https://www.douyin.com/search/%E5%92%8C%E5%B9%B3%E7%B2%BE%E8%8B%B1%E5%B0%8F%E7%81%AB%E4%BA%BA%E8%81%94%E5%8A%A8"
        },
        {
            index: Int32("12"),
            title: "唐宫奇案开播",
            hot: "789.2万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%94%90%E5%AE%AB%E5%A5%87%E6%A1%88%E5%BC%80%E6%92%AD"
        },
        {
            index: Int32("13"),
            title: "电饭锅能帮抢票是谣言",
            hot: "784.8万",
            label: "16",
            url: "https://www.douyin.com/search/%E7%94%B5%E9%A5%AD%E9%94%85%E8%83%BD%E5%B8%AE%E6%8A%A2%E7%A5%A8%E6%98%AF%E8%B0%A3%E8%A8%80"
        },
        {
            index: Int32("14"),
            title: "非遗祈福百景图",
            hot: "778.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E9%9D%9E%E9%81%97%E7%A5%88%E7%A6%8F%E7%99%BE%E6%99%AF%E5%9B%BE"
        },
        {
            index: Int32("15"),
            title: "勇士老鹰完成交易",
            hot: "774.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%8B%87%E5%A3%AB%E8%80%81%E9%B9%B0%E5%AE%8C%E6%88%90%E4%BA%A4%E6%98%93"
        },
        {
            index: Int32("16"),
            title: "浓眉被交易至奇才",
            hot: "774.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%B5%93%E7%9C%89%E8%A2%AB%E4%BA%A4%E6%98%93%E8%87%B3%E5%A5%87%E6%89%8D"
        },
        {
            index: Int32("17"),
            title: "中方回应长和集团将发起国际仲裁",
            hot: "772.6万",
            label: "1",
            url: "https://www.douyin.com/search/%E4%B8%AD%E6%96%B9%E5%9B%9E%E5%BA%94%E9%95%BF%E5%92%8C%E9%9B%86%E5%9B%A2%E5%B0%86%E5%8F%91%E8%B5%B7%E5%9B%BD%E9%99%85%E4%BB%B2%E8%A3%81"
        },
        {
            index: Int32("18"),
            title: "王者荣耀新春版本前瞻",
            hot: "771.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%8E%8B%E8%80%85%E8%8D%A3%E8%80%80%E6%96%B0%E6%98%A5%E7%89%88%E6%9C%AC%E5%89%8D%E7%9E%BB"
        },
        {
            index: Int32("19"),
            title: "唱相亲相爱迎团圆新年",
            hot: "769万",
            label: "9",
            url: "https://www.douyin.com/search/%E5%94%B1%E7%9B%B8%E4%BA%B2%E7%9B%B8%E7%88%B1%E8%BF%8E%E5%9B%A2%E5%9C%86%E6%96%B0%E5%B9%B4"
        },
        {
            index: Int32("20"),
            title: "中国网络视听盛典",
            hot: "768.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B8%AD%E5%9B%BD%E7%BD%91%E7%BB%9C%E8%A7%86%E5%90%AC%E7%9B%9B%E5%85%B8"
        },
        {
            index: Int32("21"),
            title: "金铲铲之战福星最强阵容",
            hot: "768.2万",
            label: "1",
            url: "https://www.douyin.com/search/%E9%87%91%E9%93%B2%E9%93%B2%E4%B9%8B%E6%88%98%E7%A6%8F%E6%98%9F%E6%9C%80%E5%BC%BA%E9%98%B5%E5%AE%B9"
        },
        {
            index: Int32("22"),
            title: "惊蛰无声国安小队黑衣就位",
            hot: "768.2万",
            label: "5",
            url: "https://www.douyin.com/search/%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0%E5%9B%BD%E5%AE%89%E5%B0%8F%E9%98%9F%E9%BB%91%E8%A1%A3%E5%B0%B1%E4%BD%8D"
        },
        {
            index: Int32("23"),
            title: "大哥白椿终于回来了",
            hot: "767.7万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%A7%E5%93%A5%E7%99%BD%E6%A4%BF%E7%BB%88%E4%BA%8E%E5%9B%9E%E6%9D%A5%E4%BA%86"
        },
        {
            index: Int32("24"),
            title: "冯大爷是我的春晚后台人脉",
            hot: "767.7万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%86%AF%E5%A4%A7%E7%88%B7%E6%98%AF%E6%88%91%E7%9A%84%E6%98%A5%E6%99%9A%E5%90%8E%E5%8F%B0%E4%BA%BA%E8%84%89"
        },
        {
            index: Int32("25"),
            title: "白鹿手搓李佩仪好曼妙",
            hot: "767.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%99%BD%E9%B9%BF%E6%89%8B%E6%90%93%E6%9D%8E%E4%BD%A9%E4%BB%AA%E5%A5%BD%E6%9B%BC%E5%A6%99"
        },
        {
            index: Int32("26"),
            title: "于蕾连续四年执导春晚",
            hot: "767.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E4%BA%8E%E8%95%BE%E8%BF%9E%E7%BB%AD%E5%9B%9B%E5%B9%B4%E6%89%A7%E5%AF%BC%E6%98%A5%E6%99%9A"
        },
        {
            index: Int32("27"),
            title: "记录我的一半一半",
            hot: "767.4万",
            label: "9",
            url: "https://www.douyin.com/search/%E8%AE%B0%E5%BD%95%E6%88%91%E7%9A%84%E4%B8%80%E5%8D%8A%E4%B8%80%E5%8D%8A"
        },
        {
            index: Int32("28"),
            title: "新年马“甲”手势舞我先跳",
            hot: "767.3万",
            label: "9",
            url: "https://www.douyin.com/search/%E6%96%B0%E5%B9%B4%E9%A9%AC%E2%80%9C%E7%94%B2%E2%80%9D%E6%89%8B%E5%8A%BF%E8%88%9E%E6%88%91%E5%85%88%E8%B7%B3"
        },
        {
            index: Int32("29"),
            title: "岳雨婷跳舞我给到一个夯",
            hot: "766.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%B2%B3%E9%9B%A8%E5%A9%B7%E8%B7%B3%E8%88%9E%E6%88%91%E7%BB%99%E5%88%B0%E4%B8%80%E4%B8%AA%E5%A4%AF"
        },
        {
            index: Int32("30"),
            title: "翟一莹演夏之星我是真想看",
            hot: "765.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BF%9F%E4%B8%80%E8%8E%B9%E6%BC%94%E5%A4%8F%E4%B9%8B%E6%98%9F%E6%88%91%E6%98%AF%E7%9C%9F%E6%83%B3%E7%9C%8B"
        },
        {
            index: Int32("31"),
            title: "奶奶牌限量手工AJ超酷的",
            hot: "765.6万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%A5%B6%E5%A5%B6%E7%89%8C%E9%99%90%E9%87%8F%E6%89%8B%E5%B7%A5AJ%E8%B6%85%E9%85%B7%E7%9A%84"
        },
        {
            index: Int32("32"),
            title: "鸣潮3.1版本正式上线",
            hot: "765.4万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%B8%A3%E6%BD%AE3.1%E7%89%88%E6%9C%AC%E6%AD%A3%E5%BC%8F%E4%B8%8A%E7%BA%BF"
        },
        {
            index: Int32("33"),
            title: "梦龙乐队中国巡演官宣",
            hot: "765.1万",
            label: "1",
            url: "https://www.douyin.com/search/%E6%A2%A6%E9%BE%99%E4%B9%90%E9%98%9F%E4%B8%AD%E5%9B%BD%E5%B7%A1%E6%BC%94%E5%AE%98%E5%AE%A3"
        },
        {
            index: Int32("34"),
            title: "江疏影新剧破碎感下的人间清醒",
            hot: "765万",
            label: "8",
            url: "https://www.douyin.com/search/%E6%B1%9F%E7%96%8F%E5%BD%B1%E6%96%B0%E5%89%A7%E7%A0%B4%E7%A2%8E%E6%84%9F%E4%B8%8B%E7%9A%84%E4%BA%BA%E9%97%B4%E6%B8%85%E9%86%92"
        },
        {
            index: Int32("35"),
            title: "美伊谈判濒临破裂后敲定地点",
            hot: "764.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%8A%E8%B0%88%E5%88%A4%E6%BF%92%E4%B8%B4%E7%A0%B4%E8%A3%82%E5%90%8E%E6%95%B2%E5%AE%9A%E5%9C%B0%E7%82%B9"
        },
        {
            index: Int32("36"),
            title: "镜头一拉就长大了",
            hot: "764.4万",
            label: "9",
            url: "https://www.douyin.com/search/%E9%95%9C%E5%A4%B4%E4%B8%80%E6%8B%89%E5%B0%B1%E9%95%BF%E5%A4%A7%E4%BA%86"
        },
        {
            index: Int32("37"),
            title: "太平年郭威要立养子当太子",
            hot: "763.9万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%A4%AA%E5%B9%B3%E5%B9%B4%E9%83%AD%E5%A8%81%E8%A6%81%E7%AB%8B%E5%85%BB%E5%AD%90%E5%BD%93%E5%A4%AA%E5%AD%90"
        },
        {
            index: Int32("38"),
            title: "跟着凌云探秘泉州百年狮阵",
            hot: "763.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%B7%9F%E7%9D%80%E5%87%8C%E4%BA%91%E6%8E%A2%E7%A7%98%E6%B3%89%E5%B7%9E%E7%99%BE%E5%B9%B4%E7%8B%AE%E9%98%B5"
        },
        {
            index: Int32("39"),
            title: "长大了带父母来北京旅游圆梦",
            hot: "763.5万",
            label: "0",
            url: "https://www.douyin.com/search/%E9%95%BF%E5%A4%A7%E4%BA%86%E5%B8%A6%E7%88%B6%E6%AF%8D%E6%9D%A5%E5%8C%97%E4%BA%AC%E6%97%85%E6%B8%B8%E5%9C%86%E6%A2%A6"
        },
        {
            index: Int32("40"),
            title: "十二摇手势舞挑战",
            hot: "763.5万",
            label: "9",
            url: "https://www.douyin.com/search/%E5%8D%81%E4%BA%8C%E6%91%87%E6%89%8B%E5%8A%BF%E8%88%9E%E6%8C%91%E6%88%98"
        },
        {
            index: Int32("41"),
            title: "郑恺你别抽象了我害怕",
            hot: "763万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%83%91%E6%81%BA%E4%BD%A0%E5%88%AB%E6%8A%BD%E8%B1%A1%E4%BA%86%E6%88%91%E5%AE%B3%E6%80%95"
        },
        {
            index: Int32("42"),
            title: "猴哥来送新春祝福",
            hot: "762.9万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8C%B4%E5%93%A5%E6%9D%A5%E9%80%81%E6%96%B0%E6%98%A5%E7%A5%9D%E7%A6%8F"
        },
        {
            index: Int32("43"),
            title: "生命树张勤勤不舍女儿远嫁",
            hot: "762.1万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%9F%E5%91%BD%E6%A0%91%E5%BC%A0%E5%8B%A4%E5%8B%A4%E4%B8%8D%E8%88%8D%E5%A5%B3%E5%84%BF%E8%BF%9C%E5%AB%81"
        },
        {
            index: Int32("44"),
            title: "张艺凡求粉丝删掉雷霆二创",
            hot: "762万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%BC%A0%E8%89%BA%E5%87%A1%E6%B1%82%E7%B2%89%E4%B8%9D%E5%88%A0%E6%8E%89%E9%9B%B7%E9%9C%86%E4%BA%8C%E5%88%9B"
        },
        {
            index: Int32("45"),
            title: "张翅雪地照片欧巴味太足了",
            hot: "762万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%BC%A0%E7%BF%85%E9%9B%AA%E5%9C%B0%E7%85%A7%E7%89%87%E6%AC%A7%E5%B7%B4%E5%91%B3%E5%A4%AA%E8%B6%B3%E4%BA%86"
        },
        {
            index: Int32("46"),
            title: "蛋仔荔枝皮肤曝光",
            hot: "762万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%9B%8B%E4%BB%94%E8%8D%94%E6%9E%9D%E7%9A%AE%E8%82%A4%E6%9B%9D%E5%85%89"
        },
        {
            index: Int32("47"),
            title: "听单依纯立春断舍离",
            hot: "761.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%AC%E5%8D%95%E4%BE%9D%E7%BA%AF%E7%AB%8B%E6%98%A5%E6%96%AD%E8%88%8D%E7%A6%BB"
        },
        {
            index: Int32("48"),
            title: "年少有为男人吃醋更抓马",
            hot: "761万",
            label: "5",
            url: "https://www.douyin.com/search/%E5%B9%B4%E5%B0%91%E6%9C%89%E4%B8%BA%E7%94%B7%E4%BA%BA%E5%90%83%E9%86%8B%E6%9B%B4%E6%8A%93%E9%A9%AC"
        },
        {
            index: Int32("49"),
            title: "刘玫白天嘴硬深夜泪崩心碎",
            hot: "760.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%88%98%E7%8E%AB%E7%99%BD%E5%A4%A9%E5%98%B4%E7%A1%AC%E6%B7%B1%E5%A4%9C%E6%B3%AA%E5%B4%A9%E5%BF%83%E7%A2%8E"
        },
        {
            index: Int32("50"),
            title: "短剧演员红毯视频完播率100%",
            hot: "758.7万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%9F%AD%E5%89%A7%E6%BC%94%E5%91%98%E7%BA%A2%E6%AF%AF%E8%A7%86%E9%A2%91%E5%AE%8C%E6%92%AD%E7%8E%87100%25"
        },
        {
            index: Int32("51"),
            title: "不二之臣剧组0210抖音直播",
            hot: "744万",
            label: "8",
            url: "https://www.douyin.com/search/%E4%B8%8D%E4%BA%8C%E4%B9%8B%E8%87%A3%E5%89%A7%E7%BB%840210%E6%8A%96%E9%9F%B3%E7%9B%B4%E6%92%AD"
        }
    ],
    createdAt: ISODate("2026-02-05T10:31:38.482Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);
db.getCollection("hot_news_main").insert([ {
    _id: ObjectId("69858bc56d84f72baba8f56b"),
    success: true,
    title: "抖音",
    subtitle: "抖音热点",
    data: [
        {
            index: Int32("1"),
            title: "总书记寄语中国体育健儿",
            hot: "0万",
            label: "0",
            url: "https://www.douyin.com/search/%E6%80%BB%E4%B9%A6%E8%AE%B0%E5%AF%84%E8%AF%AD%E4%B8%AD%E5%9B%BD%E4%BD%93%E8%82%B2%E5%81%A5%E5%84%BF"
        },
        {
            index: Int32("2"),
            title: "美国伊朗谈判今日举行",
            hot: "1236.3万",
            label: "0",
            url: "https://www.douyin.com/search/%E7%BE%8E%E5%9B%BD%E4%BC%8A%E6%9C%97%E8%B0%88%E5%88%A4%E4%BB%8A%E6%97%A5%E4%B8%BE%E8%A1%8C"
        },
        {
            index: Int32("3"),
            title: "董亦军被追授时代楷模称号",
            hot: "1144.6万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%91%A3%E4%BA%A6%E5%86%9B%E8%A2%AB%E8%BF%BD%E6%8E%88%E6%97%B6%E4%BB%A3%E6%A5%B7%E6%A8%A1%E7%A7%B0%E5%8F%B7"
        },
        {
            index: Int32("4"),
            title: "“反向过年”成为新潮",
            hot: "1115.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E2%80%9C%E5%8F%8D%E5%90%91%E8%BF%87%E5%B9%B4%E2%80%9D%E6%88%90%E4%B8%BA%E6%96%B0%E6%BD%AE"
        },
        {
            index: Int32("5"),
            title: "苏翊鸣晋级大跳台决赛",
            hot: "1111.1万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%8B%8F%E7%BF%8A%E9%B8%A3%E6%99%8B%E7%BA%A7%E5%A4%A7%E8%B7%B3%E5%8F%B0%E5%86%B3%E8%B5%9B"
        },
        {
            index: Int32("6"),
            title: "橘时到吉时到",
            hot: "1054万",
            label: "1",
            url: "https://www.douyin.com/search/%E6%A9%98%E6%97%B6%E5%88%B0%E5%90%89%E6%97%B6%E5%88%B0"
        },
        {
            index: Int32("7"),
            title: "这届精选创作者宠粉太全面了",
            hot: "1029.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E8%BF%99%E5%B1%8A%E7%B2%BE%E9%80%89%E5%88%9B%E4%BD%9C%E8%80%85%E5%AE%A0%E7%B2%89%E5%A4%AA%E5%85%A8%E9%9D%A2%E4%BA%86"
        },
        {
            index: Int32("8"),
            title: "留子回国过年吃啥都香",
            hot: "918.5万",
            label: "1",
            url: "https://www.douyin.com/search/%E7%95%99%E5%AD%90%E5%9B%9E%E5%9B%BD%E8%BF%87%E5%B9%B4%E5%90%83%E5%95%A5%E9%83%BD%E9%A6%99"
        },
        {
            index: Int32("9"),
            title: "海南省委原秘书长倪强被双开",
            hot: "914.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E6%B5%B7%E5%8D%97%E7%9C%81%E5%A7%94%E5%8E%9F%E7%A7%98%E4%B9%A6%E9%95%BF%E5%80%AA%E5%BC%BA%E8%A2%AB%E5%8F%8C%E5%BC%80"
        },
        {
            index: Int32("10"),
            title: "冬日跑步装备大赏",
            hot: "912.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%86%AC%E6%97%A5%E8%B7%91%E6%AD%A5%E8%A3%85%E5%A4%87%E5%A4%A7%E8%B5%8F"
        },
        {
            index: Int32("11"),
            title: "媒体：立陶宛嘴上认错还不够",
            hot: "908.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AA%92%E4%BD%93%EF%BC%9A%E7%AB%8B%E9%99%B6%E5%AE%9B%E5%98%B4%E4%B8%8A%E8%AE%A4%E9%94%99%E8%BF%98%E4%B8%8D%E5%A4%9F"
        },
        {
            index: Int32("12"),
            title: "我的刀盾",
            hot: "908.3万",
            label: "17",
            url: "https://www.douyin.com/search/%E6%88%91%E7%9A%84%E5%88%80%E7%9B%BE"
        },
        {
            index: Int32("13"),
            title: "重庆市政协原副主席段成刚被公诉",
            hot: "906.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E9%87%8D%E5%BA%86%E5%B8%82%E6%94%BF%E5%8D%8F%E5%8E%9F%E5%89%AF%E4%B8%BB%E5%B8%AD%E6%AE%B5%E6%88%90%E5%88%9A%E8%A2%AB%E5%85%AC%E8%AF%89"
        },
        {
            index: Int32("14"),
            title: "专家辟谣“一瓶饮料快速解酒”",
            hot: "890.1万",
            label: "16",
            url: "https://www.douyin.com/search/%E4%B8%93%E5%AE%B6%E8%BE%9F%E8%B0%A3%E2%80%9C%E4%B8%80%E7%93%B6%E9%A5%AE%E6%96%99%E5%BF%AB%E9%80%9F%E8%A7%A3%E9%85%92%E2%80%9D"
        },
        {
            index: Int32("15"),
            title: "A股",
            hot: "889.6万",
            label: "6",
            url: "https://www.douyin.com/search/A%E8%82%A1"
        },
        {
            index: Int32("16"),
            title: "商业航天何以“一飞冲天”",
            hot: "874.4万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%95%86%E4%B8%9A%E8%88%AA%E5%A4%A9%E4%BD%95%E4%BB%A5%E2%80%9C%E4%B8%80%E9%A3%9E%E5%86%B2%E5%A4%A9%E2%80%9D"
        },
        {
            index: Int32("17"),
            title: "湖人终结76人5连胜",
            hot: "870.2万",
            label: "1",
            url: "https://www.douyin.com/search/%E6%B9%96%E4%BA%BA%E7%BB%88%E7%BB%9376%E4%BA%BA5%E8%BF%9E%E8%83%9C"
        },
        {
            index: Int32("18"),
            title: "李佩仪目睹闺蜜自杀",
            hot: "866.9万",
            label: "11",
            url: "https://www.douyin.com/search/%E6%9D%8E%E4%BD%A9%E4%BB%AA%E7%9B%AE%E7%9D%B9%E9%97%BA%E8%9C%9C%E8%87%AA%E6%9D%80"
        },
        {
            index: Int32("19"),
            title: "中方回应长和集团将发起国际仲裁",
            hot: "866万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B8%AD%E6%96%B9%E5%9B%9E%E5%BA%94%E9%95%BF%E5%92%8C%E9%9B%86%E5%9B%A2%E5%B0%86%E5%8F%91%E8%B5%B7%E5%9B%BD%E9%99%85%E4%BB%B2%E8%A3%81"
        },
        {
            index: Int32("20"),
            title: "外交部回应普京计划访华",
            hot: "854.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%A4%96%E4%BA%A4%E9%83%A8%E5%9B%9E%E5%BA%94%E6%99%AE%E4%BA%AC%E8%AE%A1%E5%88%92%E8%AE%BF%E5%8D%8E"
        },
        {
            index: Int32("21"),
            title: "网剧成何体统开播",
            hot: "794.8万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%BD%91%E5%89%A7%E6%88%90%E4%BD%95%E4%BD%93%E7%BB%9F%E5%BC%80%E6%92%AD"
        },
        {
            index: Int32("22"),
            title: "多地漫展禁止cos名侦探柯南角色",
            hot: "789.2万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%A4%9A%E5%9C%B0%E6%BC%AB%E5%B1%95%E7%A6%81%E6%AD%A2cos%E5%90%8D%E4%BE%A6%E6%8E%A2%E6%9F%AF%E5%8D%97%E8%A7%92%E8%89%B2"
        },
        {
            index: Int32("23"),
            title: "郑泽晖任深圳市副市长",
            hot: "785.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%83%91%E6%B3%BD%E6%99%96%E4%BB%BB%E6%B7%B1%E5%9C%B3%E5%B8%82%E5%89%AF%E5%B8%82%E9%95%BF"
        },
        {
            index: Int32("24"),
            title: "邓超终于有抖音了",
            hot: "778.7万",
            label: "1",
            url: "https://www.douyin.com/search/%E9%82%93%E8%B6%85%E7%BB%88%E4%BA%8E%E6%9C%89%E6%8A%96%E9%9F%B3%E4%BA%86"
        },
        {
            index: Int32("25"),
            title: "分身搭子陪你过大年",
            hot: "778.6万",
            label: "9",
            url: "https://www.douyin.com/search/%E5%88%86%E8%BA%AB%E6%90%AD%E5%AD%90%E9%99%AA%E4%BD%A0%E8%BF%87%E5%A4%A7%E5%B9%B4"
        },
        {
            index: Int32("26"),
            title: "盘点生命树的隐藏剧情线",
            hot: "777.5万",
            label: "8",
            url: "https://www.douyin.com/search/%E7%9B%98%E7%82%B9%E7%94%9F%E5%91%BD%E6%A0%91%E7%9A%84%E9%9A%90%E8%97%8F%E5%89%A7%E6%83%85%E7%BA%BF"
        },
        {
            index: Int32("27"),
            title: "蔡徐坤全新专辑听后感",
            hot: "776.9万",
            label: "3",
            url: "https://www.douyin.com/search/%E8%94%A1%E5%BE%90%E5%9D%A4%E5%85%A8%E6%96%B0%E4%B8%93%E8%BE%91%E5%90%AC%E5%90%8E%E6%84%9F"
        },
        {
            index: Int32("28"),
            title: "飞驰3沈腾沙溢打球各有各的好笑",
            hot: "775.2万",
            label: "5",
            url: "https://www.douyin.com/search/%E9%A3%9E%E9%A9%B03%E6%B2%88%E8%85%BE%E6%B2%99%E6%BA%A2%E6%89%93%E7%90%83%E5%90%84%E6%9C%89%E5%90%84%E7%9A%84%E5%A5%BD%E7%AC%91"
        },
        {
            index: Int32("29"),
            title: "大主宰2武祖林动惊喜登场",
            hot: "774.3万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%A4%A7%E4%B8%BB%E5%AE%B02%E6%AD%A6%E7%A5%96%E6%9E%97%E5%8A%A8%E6%83%8A%E5%96%9C%E7%99%BB%E5%9C%BA"
        },
        {
            index: Int32("30"),
            title: "夜色正浓高质感太顶了",
            hot: "774.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%A4%9C%E8%89%B2%E6%AD%A3%E6%B5%93%E9%AB%98%E8%B4%A8%E6%84%9F%E5%A4%AA%E9%A1%B6%E4%BA%86"
        },
        {
            index: Int32("31"),
            title: "电影惊蛰无声全员有嫌疑",
            hot: "774.1万",
            label: "5",
            url: "https://www.douyin.com/search/%E7%94%B5%E5%BD%B1%E6%83%8A%E8%9B%B0%E6%97%A0%E5%A3%B0%E5%85%A8%E5%91%98%E6%9C%89%E5%AB%8C%E7%96%91"
        },
        {
            index: Int32("32"),
            title: "美众议院上演骂战",
            hot: "774万",
            label: "3",
            url: "https://www.douyin.com/search/%E7%BE%8E%E4%BC%97%E8%AE%AE%E9%99%A2%E4%B8%8A%E6%BC%94%E9%AA%82%E6%88%98"
        },
        {
            index: Int32("33"),
            title: "当困难来临的时候",
            hot: "773.8万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%BD%93%E5%9B%B0%E9%9A%BE%E6%9D%A5%E4%B8%B4%E7%9A%84%E6%97%B6%E5%80%99"
        },
        {
            index: Int32("34"),
            title: "马斯克怒批西班牙首相",
            hot: "772.9万",
            label: "0",
            url: "https://www.douyin.com/search/%E9%A9%AC%E6%96%AF%E5%85%8B%E6%80%92%E6%89%B9%E8%A5%BF%E7%8F%AD%E7%89%99%E9%A6%96%E7%9B%B8"
        },
        {
            index: Int32("35"),
            title: "在三角洲市集打卡陈泽",
            hot: "772.1万",
            label: "1",
            url: "https://www.douyin.com/search/%E5%9C%A8%E4%B8%89%E8%A7%92%E6%B4%B2%E5%B8%82%E9%9B%86%E6%89%93%E5%8D%A1%E9%99%88%E6%B3%BD"
        },
        {
            index: Int32("36"),
            title: "唐宫奇案剧宣闯入ai赛道",
            hot: "771.8万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%94%90%E5%AE%AB%E5%A5%87%E6%A1%88%E5%89%A7%E5%AE%A3%E9%97%AF%E5%85%A5ai%E8%B5%9B%E9%81%93"
        },
        {
            index: Int32("37"),
            title: "官方回应男子从着火电车连救3人",
            hot: "771万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%AE%98%E6%96%B9%E5%9B%9E%E5%BA%94%E7%94%B7%E5%AD%90%E4%BB%8E%E7%9D%80%E7%81%AB%E7%94%B5%E8%BD%A6%E8%BF%9E%E6%95%913%E4%BA%BA"
        },
        {
            index: Int32("38"),
            title: "恋与深空喜迎财神",
            hot: "770.2万",
            label: "1",
            url: "https://www.douyin.com/search/%E6%81%8B%E4%B8%8E%E6%B7%B1%E7%A9%BA%E5%96%9C%E8%BF%8E%E8%B4%A2%E7%A5%9E"
        },
        {
            index: Int32("39"),
            title: "快过年了给大家摇一个",
            hot: "769.7万",
            label: "9",
            url: "https://www.douyin.com/search/%E5%BF%AB%E8%BF%87%E5%B9%B4%E4%BA%86%E7%BB%99%E5%A4%A7%E5%AE%B6%E6%91%87%E4%B8%80%E4%B8%AA"
        },
        {
            index: Int32("40"),
            title: "彩虹霉豆腐申请出战",
            hot: "769万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%BD%A9%E8%99%B9%E9%9C%89%E8%B1%86%E8%85%90%E7%94%B3%E8%AF%B7%E5%87%BA%E6%88%98"
        },
        {
            index: Int32("41"),
            title: "冯大爷是我的春晚后台人脉",
            hot: "768.8万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%86%AF%E5%A4%A7%E7%88%B7%E6%98%AF%E6%88%91%E7%9A%84%E6%98%A5%E6%99%9A%E5%90%8E%E5%8F%B0%E4%BA%BA%E8%84%89"
        },
        {
            index: Int32("42"),
            title: "奥利给首支人物故事短片",
            hot: "768.6万",
            label: "8",
            url: "https://www.douyin.com/search/%E5%A5%A5%E5%88%A9%E7%BB%99%E9%A6%96%E6%94%AF%E4%BA%BA%E7%89%A9%E6%95%85%E4%BA%8B%E7%9F%AD%E7%89%87"
        },
        {
            index: Int32("43"),
            title: "吴克群携贵州爱心企业助力菜农",
            hot: "768.5万",
            label: "3",
            url: "https://www.douyin.com/search/%E5%90%B4%E5%85%8B%E7%BE%A4%E6%90%BA%E8%B4%B5%E5%B7%9E%E7%88%B1%E5%BF%83%E4%BC%81%E4%B8%9A%E5%8A%A9%E5%8A%9B%E8%8F%9C%E5%86%9C"
        },
        {
            index: Int32("44"),
            title: "奶奶牌限量手工AJ超酷的",
            hot: "768.4万",
            label: "17",
            url: "https://www.douyin.com/search/%E5%A5%B6%E5%A5%B6%E7%89%8C%E9%99%90%E9%87%8F%E6%89%8B%E5%B7%A5AJ%E8%B6%85%E9%85%B7%E7%9A%84"
        },
        {
            index: Int32("45"),
            title: "金铲铲之战福星最强阵容",
            hot: "768.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%87%91%E9%93%B2%E9%93%B2%E4%B9%8B%E6%88%98%E7%A6%8F%E6%98%9F%E6%9C%80%E5%BC%BA%E9%98%B5%E5%AE%B9"
        },
        {
            index: Int32("46"),
            title: "猴哥来送新春祝福",
            hot: "767.3万",
            label: "17",
            url: "https://www.douyin.com/search/%E7%8C%B4%E5%93%A5%E6%9D%A5%E9%80%81%E6%96%B0%E6%98%A5%E7%A5%9D%E7%A6%8F"
        },
        {
            index: Int32("47"),
            title: "郑雅娴和宋雨琦一起OKOK",
            hot: "766.2万",
            label: "3",
            url: "https://www.douyin.com/search/%E9%83%91%E9%9B%85%E5%A8%B4%E5%92%8C%E5%AE%8B%E9%9B%A8%E7%90%A6%E4%B8%80%E8%B5%B7OKOK"
        },
        {
            index: Int32("48"),
            title: "丁程鑫嘎嘣一下就睡那了",
            hot: "766万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B8%81%E7%A8%8B%E9%91%AB%E5%98%8E%E5%98%A3%E4%B8%80%E4%B8%8B%E5%B0%B1%E7%9D%A1%E9%82%A3%E4%BA%86"
        },
        {
            index: Int32("49"),
            title: "被隐匿的真相开播",
            hot: "765.8万",
            label: "5",
            url: "https://www.douyin.com/search/%E8%A2%AB%E9%9A%90%E5%8C%BF%E7%9A%84%E7%9C%9F%E7%9B%B8%E5%BC%80%E6%92%AD"
        },
        {
            index: Int32("50"),
            title: "一人一首悟空",
            hot: "765.7万",
            label: "0",
            url: "https://www.douyin.com/search/%E4%B8%80%E4%BA%BA%E4%B8%80%E9%A6%96%E6%82%9F%E7%A9%BA"
        },
        {
            index: Int32("51"),
            title: "徐艺洋骗黄子韬跳水",
            hot: "765.6万",
            label: "0",
            url: "https://www.douyin.com/search/%E5%BE%90%E8%89%BA%E6%B4%8B%E9%AA%97%E9%BB%84%E5%AD%90%E9%9F%AC%E8%B7%B3%E6%B0%B4"
        }
    ],
    createdAt: ISODate("2026-02-06T06:35:49.641Z"),
    type: "douyinhot",
    _class: "com.example.yoyo_data.common.document.HotNewsMain"
} ]);

// ----------------------------
// Collection structure for social_comments
// ----------------------------
db.getCollection("social_comments").drop();
db.createCollection("social_comments");

// ----------------------------
// Documents of social_comments
// ----------------------------
db.getCollection("social_comments").insert([ {
    _id: ObjectId("697038ac94e9419e0d116039"),
    comment_id: "comment_ObZ1wLpADugsMWA_",
    post_id: "696eee0b9a79c062f8cccc50",
    user_id: Int32("1"),
    content: "好想去，1111111\n",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T02:23:40.493Z")
} ]);
db.getCollection("social_comments").insert([ {
    _id: ObjectId("69703d497ebb1b01a512d01b"),
    comment_id: "comment_mnrA7NL_sTqZay5x",
    post_id: "696eee0b9a79c062f8cccc50",
    user_id: Int32("1"),
    content: "11111111",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T02:43:21.747Z")
} ]);
db.getCollection("social_comments").insert([ {
    _id: ObjectId("69703f287ebb1b01a512d01c"),
    comment_id: "comment_7vkQI-Af7-fh1s58",
    post_id: "696eee0b9a79c062f8cccc50",
    user_id: Int32("1"),
    content: "232222222222",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T02:51:20.814Z")
} ]);
db.getCollection("social_comments").insert([ {
    _id: ObjectId("697068e5a3286926c0ef3f5d"),
    comment_id: "comment_TtMivbwr6KXwWULm",
    post_id: "696eee0b9a79c062f8cccc50",
    user_id: Int32("1"),
    content: "23",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T05:49:25.374Z")
} ]);
db.getCollection("social_comments").insert([ {
    _id: ObjectId("69706964a3286926c0ef3f5e"),
    comment_id: "comment_V9NeY5AywkPDIO3B",
    post_id: "696eee0b9a79c062f8cccc4e",
    user_id: Int32("1"),
    content: "还好看\n",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T05:51:32.518Z")
} ]);
db.getCollection("social_comments").insert([ {
    _id: ObjectId("6970749bc4d9f199ee1cfc17"),
    comment_id: "comment_hrNLB0UQSyGUEggu",
    post_id: "696eee0b9a79c062f8cccc4e",
    user_id: Int32("1"),
    content: "1111",
    parent_id: null,
    like_count: Int32("0"),
    created_at: ISODate("2026-01-21T06:39:23.749Z")
} ]);

// ----------------------------
// Collection structure for social_likes
// ----------------------------
db.getCollection("social_likes").drop();
db.createCollection("social_likes");

// ----------------------------
// Documents of social_likes
// ----------------------------
db.getCollection("social_likes").insert([ {
    _id: ObjectId("697036b794e9419e0d116038"),
    like_id: "like_daMdTCwGpNxBGGHb",
    user_id: Int32("1"),
    post_id: "696eee0b9a79c062f8cccc4f",
    created_at: ISODate("2026-01-21T02:15:19.798Z")
} ]);
db.getCollection("social_likes").insert([ {
    _id: ObjectId("6970696aa3286926c0ef3f5f"),
    like_id: "like_DfsrIJN3KTxAjNdL",
    user_id: Int32("1"),
    post_id: "696eee0b9a79c062f8cccc4e",
    created_at: ISODate("2026-01-21T05:51:38.426Z")
} ]);
db.getCollection("social_likes").insert([ {
    _id: ObjectId("6970696ba3286926c0ef3f60"),
    like_id: "like_VpZHrX5NRA-3_W76",
    user_id: Int32("1"),
    post_id: "696eee0b9a79c062f8cccc50",
    created_at: ISODate("2026-01-21T05:51:39.896Z")
} ]);

// ----------------------------
// Collection structure for social_posts
// ----------------------------
db.getCollection("social_posts").drop();
db.createCollection("social_posts");

// ----------------------------
// Documents of social_posts
// ----------------------------
db.getCollection("social_posts").insert([ {
    _id: ObjectId("696eee0b9a79c062f8cccc51"),
    post_id: "696eee0b9a79c062f8cccc4e",
    user_id: Int32("1"),
    content: "今天去了长城，风景真美！",
    media_urls: [
        "https://img95.699pic.com/photo/50136/6765.jpg_wh860.jpg"
    ],
    tags: [
        "旅行",
        "长城"
    ],
    like_count: Int32("11"),
    comment_count: Int32("2"),
    moderation_status: "approved",
    created_at: ISODate("2026-01-19T10:52:59.309Z"),
    updated_at: ISODate("2026-01-19T10:52:59.309Z"),
    view_count: 100,
    title: "北京一日游11"
} ]);
db.getCollection("social_posts").insert([ {
    _id: ObjectId("696eee0b9a79c062f8cccc52"),
    post_id: "696eee0b9a79c062f8cccc4f",
    user_id: Int32("1"),
    content: "在故宫里拍了很多照片，历史感十足！",
    media_urls: [
        "https://bpic.588ku.com/back_origin_min_pic/19/09/23/593eae9555db91d7908839deecd452da.jpg"
    ],
    tags: [
        "旅行",
        "故宫"
    ],
    like_count: Int32("16"),
    comment_count: Int32("0"),
    moderation_status: "approved",
    created_at: ISODate("2026-01-19T22:52:59.309Z"),
    updated_at: ISODate("2026-01-19T22:52:59.309Z"),
    view_count: 89,
    title: "故宫旅行"
} ]);
db.getCollection("social_posts").insert([ {
    _id: ObjectId("696eee0b9a79c062f8cccc53"),
    post_id: "696eee0b9a79c062f8cccc50",
    user_id: Int32("2"),
    content: "西湖的美景让人流连忘返！",
    media_urls: [
        "https://youimg1.c-ctrip.com/target/100d14000000vu15e552D_D_10000_1200.jpg?proc=autoorient"
    ],
    tags: [
        "旅行",
        "西湖"
    ],
    like_count: Int32("9"),
    comment_count: Int32("4"),
    moderation_status: "approved",
    created_at: ISODate("2026-01-20T04:52:59.309Z"),
    updated_at: ISODate("2026-01-20T04:52:59.309Z"),
    view_count: 78,
    title: "西湖观赏"
} ]);

// ----------------------------
// Collection structure for tool_call_logs
// ----------------------------
db.getCollection("tool_call_logs").drop();
db.createCollection("tool_call_logs");
db.getCollection("tool_call_logs").createIndex({
    session_id: Int32("1"),
    created_at: Int32("-1")
}, {
    name: "session_id_1_created_at_-1"
});
db.getCollection("tool_call_logs").createIndex({
    user_id: Int32("1"),
    tool_name: Int32("1"),
    created_at: Int32("-1")
}, {
    name: "user_id_1_tool_name_1_created_at_-1"
});
db.getCollection("tool_call_logs").createIndex({
    created_at: Int32("-1")
}, {
    name: "created_at_-1"
});

// ----------------------------
// Documents of tool_call_logs
// ----------------------------
db.getCollection("tool_call_logs").insert([ {
    _id: ObjectId("69a10ff8e829f88a7ce9e8f9"),
    log_id: "log_-MR2b8U8Gs4XJEZq",
    session_id: "session_JrRZOmBH57REbGtwfegBGA",
    tool_name: "intent_detection",
    input_params: {
        message: "故宫有什么好玩的？"
    },
    output_result: "info_query",
    execution_time_ms: 1133.02063941956,
    status: "success",
    created_at: ISODate("2026-02-27T03:31:04.071Z")
} ]);
db.getCollection("tool_call_logs").insert([ {
    _id: ObjectId("69a13259e829f88a7ce9e8fd"),
    log_id: "log_4bj4ND3mituajw7-",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    tool_name: "intent_detection",
    input_params: {
        message: "你好啊"
    },
    output_result: "general_chat",
    execution_time_ms: 637.154817581177,
    status: "success",
    created_at: ISODate("2026-02-27T05:57:45.124Z")
} ]);
db.getCollection("tool_call_logs").insert([ {
    _id: ObjectId("69a1326de829f88a7ce9e900"),
    log_id: "log_MKOARjzbNDNt6Lkj",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    tool_name: "intent_detection",
    input_params: {
        message: "想去南京万"
    },
    output_result: "trip_planning",
    execution_time_ms: 624.313116073608,
    status: "success",
    created_at: ISODate("2026-02-27T05:58:05.917Z")
} ]);
db.getCollection("tool_call_logs").insert([ {
    _id: ObjectId("69a13288e829f88a7ce9e903"),
    log_id: "log_hfQ97I_ByMqhKczy",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    tool_name: "intent_detection",
    input_params: {
        message: "南京，2月28日，旅行一天，自然风光和历史文化"
    },
    output_result: "trip_planning",
    execution_time_ms: 993.242502212524,
    status: "success",
    created_at: ISODate("2026-02-27T05:58:32.071Z")
} ]);
db.getCollection("tool_call_logs").insert([ {
    _id: ObjectId("69a1328ce829f88a7ce9e906"),
    log_id: "log_E6TmVg2CgiP6E-nQ",
    session_id: "session_XUxnUpeapnGb38vg_PpL8A",
    tool_name: "intent_detection",
    input_params: {
        message: "上海2日游"
    },
    output_result: "trip_planning",
    execution_time_ms: 421.96249961853,
    status: "success",
    created_at: ISODate("2026-02-27T05:58:36.782Z")
} ]);

// ----------------------------
// Collection structure for travel_plans
// ----------------------------
db.getCollection("travel_plans").drop();
db.createCollection("travel_plans");
db.getCollection("travel_plans").createIndex({
    user_id: Int32("1"),
    created_at: Int32("-1")
}, {
    name: "user_id_1_created_at_-1"
});
db.getCollection("travel_plans").createIndex({
    plan_id: Int32("1")
}, {
    name: "plan_id_1",
    unique: true
});
db.getCollection("travel_plans").createIndex({
    session_id: Int32("1")
}, {
    name: "session_id_1"
});
db.getCollection("travel_plans").createIndex({
    city: Int32("1"),
    start_date: Int32("-1")
}, {
    name: "city_1_start_date_-1"
});

// ----------------------------
// Documents of travel_plans
// ----------------------------
db.getCollection("travel_plans").insert([ {
    _id: ObjectId("696f2b425c4dc4fb68d5cebe"),
    city: "厦门",
    start_date: "2026-01-20",
    end_date: "2026-01-21",
    days: [
        {
            date: "2026-01-20",
            day_index: Int32("0"),
            description: "第1天行程概述：参观筼筜湖、仙岳山、厦门园林植物园，体验厦门的自然风光。",
            transportation: "公共交通",
            accommodation: "经济型酒店",
            hotel: {
                name: "佳佳旅馆(风景湖公园店)",
                address: "灌口大道809号有居便利店与中国石化中间",
                location: {
                    longitude: 118.127462,
                    latitude: 24.568558
                },
                price_range: "150-250元",
                rating: "4.0",
                distance: "距离筼筜湖5公里",
                type: "经济型酒店",
                estimated_cost: Int32("200")
            },
            attractions: [
                {
                    name: "筼筜湖",
                    address: "筼筜街道湖滨中路白鹭洲站旁",
                    location: {
                        longitude: 118.078916,
                        latitude: 24.481893
                    },
                    visit_duration: Int32("60"),
                    description: "筼筜湖是厦门市区的一个大型人工湖，周边环境优美，适合散步和休闲。",
                    category: "湖泊",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("0")
                },
                {
                    name: "仙岳山",
                    address: "仙岳公园",
                    location: {
                        longitude: 118.094218,
                        latitude: 24.495251
                    },
                    visit_duration: Int32("90"),
                    description: "仙岳山是厦门的一座小山，山顶有观景台，可以俯瞰整个厦门市区的美景。",
                    category: "山林",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("0")
                },
                {
                    name: "厦门园林植物园",
                    address: "虎园路25号",
                    location: {
                        longitude: 118.117889,
                        latitude: 24.457838
                    },
                    visit_duration: Int32("120"),
                    description: "厦门园林植物园是一座大型的植物园，拥有丰富的植物种类，是了解植物的好去处。",
                    category: "植物园",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("30")
                }
            ],
            meals: [
                {
                    type: "breakfast",
                    name: "早餐推荐",
                    address: null,
                    location: null,
                    description: "推荐在筼筜湖附近的早餐店享用传统闽南小吃，如沙茶面、海蛎煎等。",
                    estimated_cost: Int32("30")
                },
                {
                    type: "lunch",
                    name: "午餐推荐",
                    address: null,
                    location: null,
                    description: "在仙岳山附近的小餐馆品尝当地特色菜肴，如炒时蔬、海鲜炒饭等。",
                    estimated_cost: Int32("50")
                },
                {
                    type: "dinner",
                    name: "晚餐推荐",
                    address: null,
                    location: null,
                    description: "在厦门园林植物园附近的餐厅享用海鲜大餐，如清蒸海鱼、蒜蓉扇贝等。",
                    estimated_cost: Int32("80")
                }
            ]
        },
        {
            date: "2026-01-21",
            day_index: Int32("1"),
            description: "第2天行程概述：参观鼓浪屿风景名胜区、日光岩、白城沙滩，感受厦门的历史文化和海滨风光。",
            transportation: "公共交通",
            accommodation: "经济型酒店",
            hotel: {
                name: "泊捷连锁酒店(厦门火车站明发商业广场店)",
                address: "莲前西路2号莲富大厦A座3层301",
                location: {
                    longitude: 118.104542,
                    latitude: 24.468567
                },
                price_range: "200-300元",
                rating: "4.2",
                distance: "距离鼓浪屿码头3公里",
                type: "经济型酒店",
                estimated_cost: Int32("250")
            },
            attractions: [
                {
                    name: "鼓浪屿风景名胜区",
                    address: "晃岩路35-6号",
                    location: {
                        longitude: 118.295137,
                        latitude: 24.441424
                    },
                    visit_duration: Int32("180"),
                    description: "鼓浪屿是一个充满历史和文化底蕴的小岛，有许多保存完好的历史建筑和文化遗址。",
                    category: "历史文化",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("100")
                },
                {
                    name: "日光岩",
                    address: "泉州路109号",
                    location: {
                        longitude: 118.295137,
                        latitude: 24.441424
                    },
                    visit_duration: Int32("60"),
                    description: "日光岩是鼓浪屿的标志性景点，登上山顶可以俯瞰整个鼓浪屿和厦门市区的美景。",
                    category: "山林",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("30")
                },
                {
                    name: "白城沙滩",
                    address: "大学路",
                    location: {
                        longitude: 118.102536,
                        latitude: 24.432789
                    },
                    visit_duration: Int32("90"),
                    description: "白城沙滩是厦门最著名的沙滩之一，沙质细腻，海水清澈，是享受阳光和海滩的好地方。",
                    category: "海滩",
                    rating: null,
                    photos: [ ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("0")
                }
            ],
            meals: [
                {
                    type: "breakfast",
                    name: "早餐推荐",
                    address: null,
                    location: null,
                    description: "在鼓浪屿上的早餐店享用传统的福建小吃，如豆浆油条、烧饼等。",
                    estimated_cost: Int32("30")
                },
                {
                    type: "lunch",
                    name: "午餐推荐",
                    address: null,
                    location: null,
                    description: "在鼓浪屿上的海鲜餐厅品尝新鲜的海鲜，如清蒸海鱼、虾饺等。",
                    estimated_cost: Int32("60")
                },
                {
                    type: "dinner",
                    name: "晚餐推荐",
                    address: null,
                    location: null,
                    description: "在白城沙滩附近的餐厅享用烧烤和海鲜，如烤生蚝、炒蟹等。",
                    estimated_cost: Int32("80")
                }
            ]
        }
    ],
    weather_info: [
        {
            date: "2026-01-20",
            day_weather: "多云",
            night_weather: "多云",
            day_temp: Int32("17"),
            night_temp: Int32("10"),
            wind_direction: "东北风",
            wind_power: "4级"
        },
        {
            date: "2026-01-21",
            day_weather: "多云",
            night_weather: "多云",
            day_temp: Int32("14"),
            night_temp: Int32("9"),
            wind_direction: "东风",
            wind_power: "4级"
        }
    ],
    overall_suggestions: "厦门的天气较为凉爽，建议穿着长袖衣物和舒适的鞋子。第一天的行程以自然风光为主，第二天则侧重于历史文化。鼓浪屿上的景点较多，建议提前规划好路线，以免错过重要的景点。此外，厦门的美食非常丰富，不妨多尝试一些当地的特色小吃。",
    budget: {
        total_attractions: Int32("160"),
        total_hotels: Int32("450"),
        total_meals: Int32("420"),
        total_transportation: Int32("100"),
        total: Int32("1130")
    },
    title: "\"厦门旅行\"",
    user_id: Long("6"),
    status: "\"todo\"",
    plan_id: "10000010001",
    is_favorite: true,
    updated_at: ISODate("2026-02-26T17:38:02.000Z"),
    created_at: "2026-01-24 16:00:00.000"
} ]);
db.getCollection("travel_plans").insert([ {
    _id: ObjectId("69743a12b61d93a405fc68d1"),
    city: "北京",
    start_date: "2026-01-23",
    end_date: "2026-01-24",
    days: [
        {
            date: "2026-01-23",
            day_index: Int32("1"),
            description: "第一天主要参观故宫和北海公园，体验北京的历史文化。",
            transportation: "公共交通",
            accommodation: "经济型酒店",
            hotel: {
                name: "如家快捷酒店（北京天安门广场店）",
                address: "北京市东城区前门大街16号",
                location: {
                    longitude: 116.404211,
                    latitude: 39.903482
                },
                price_range: "300-500元",
                rating: "4.5",
                distance: "距离天安门广场1公里",
                type: "经济型酒店",
                estimated_cost: Int32("400")
            },
            attractions: [
                {
                    name: "故宫",
                    address: "北京市东城区景山前街4号",
                    location: {
                        longitude: 116.404211,
                        latitude: 39.921364
                    },
                    visit_duration: Int32("180"),
                    description: "故宫是中国明清两代的皇家宫殿，也是世界上现存规模最大、保存最为完整的木质结构古建筑之一。",
                    category: "历史文化",
                    rating: null,
                    photos: [
                        "https://www.bijingdi.com/uploadfile/2021/1127/20211127183901884.jpg"
                    ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("60")
                },
                {
                    name: "北海公园",
                    address: "北京市西城区文津街1号",
                    location: {
                        longitude: 116.395424,
                        latitude: 39.922997
                    },
                    visit_duration: Int32("120"),
                    description: "北海公园是北京最古老的皇家园林之一，以其精美的白塔和湖光山色著称。",
                    category: "自然风光",
                    rating: null,
                    photos: [
                        "https://bpic.588ku.com/back_list_pic/22/05/08/70a99ee84a3573bf3f5081440ca9db81.jpg"
                    ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("10")
                }
            ],
            meals: [
                {
                    type: "breakfast",
                    name: "豆汁儿焦圈",
                    address: null,
                    location: null,
                    description: "北京传统早点，豆汁儿搭配焦圈，口感独特。",
                    estimated_cost: Int32("30")
                },
                {
                    type: "lunch",
                    name: "老北京炸酱面",
                    address: null,
                    location: null,
                    description: "北京特色美食，面条劲道，酱香浓郁。",
                    estimated_cost: Int32("50")
                },
                {
                    type: "dinner",
                    name: "全聚德烤鸭",
                    address: null,
                    location: null,
                    description: "北京烤鸭的代表品牌，肉质鲜嫩，外皮酥脆。",
                    estimated_cost: Int32("150")
                }
            ]
        },
        {
            date: "2026-01-24",
            day_index: Int32("2"),
            description: "第二天主要参观圆明园，感受皇家园林的魅力。",
            transportation: "公共交通",
            accommodation: "经济型酒店",
            hotel: {
                name: "7天连锁酒店（北京西直门店）",
                address: "北京市海淀区西直门外大街18号",
                location: {
                    longitude: 116.34568,
                    latitude: 39.95382
                },
                price_range: "300-500元",
                rating: "4.5",
                distance: "距离圆明园5公里",
                type: "经济型酒店",
                estimated_cost: Int32("400")
            },
            attractions: [
                {
                    name: "圆明园",
                    address: "北京市海淀区清华西路28号",
                    location: {
                        longitude: 116.32594,
                        latitude: 39.98995
                    },
                    visit_duration: Int32("180"),
                    description: "圆明园曾是清朝皇家园林，现为遗址公园，保留了大量历史遗迹和美丽的自然景观。",
                    category: "历史文化",
                    rating: null,
                    photos: [
                        "https://img95.699pic.com/photo/60080/6931.jpg_wh860.jpg"
                    ],
                    poi_id: "",
                    image_url: null,
                    ticket_price: Int32("30")
                }
            ],
            meals: [
                {
                    type: "breakfast",
                    name: "豆浆油条",
                    address: null,
                    location: null,
                    description: "传统的中式早餐，豆浆搭配油条，营养丰富。",
                    estimated_cost: Int32("20")
                },
                {
                    type: "lunch",
                    name: "北京炸酱面",
                    address: null,
                    location: null,
                    description: "北京特色美食，面条劲道，酱香浓郁。",
                    estimated_cost: Int32("50")
                },
                {
                    type: "dinner",
                    name: "全聚德烤鸭",
                    address: null,
                    location: null,
                    description: "北京烤鸭的代表品牌，肉质鲜嫩，外皮酥脆。",
                    estimated_cost: Int32("150")
                }
            ]
        }
    ],
    weather_info: [
        {
            date: "2026-01-23",
            day_weather: "晴",
            night_weather: "多云",
            day_temp: Int32("5"),
            night_temp: Int32("-5"),
            wind_direction: "北风",
            wind_power: "1-3级"
        },
        {
            date: "2026-01-24",
            day_weather: "晴",
            night_weather: "多云",
            day_temp: Int32("6"),
            night_temp: Int32("-4"),
            wind_direction: "北风",
            wind_power: "1-3级"
        }
    ],
    overall_suggestions: "北京冬季气温较低，请注意保暖。建议穿着防寒衣物，尤其是早晚温差较大。此外，北京的公共交通非常便捷，建议使用地铁和公交出行，避免拥堵。",
    budget: {
        total_attractions: Int32("100"),
        total_hotels: Int32("800"),
        total_meals: Int32("450"),
        total_transportation: Int32("200"),
        total: Int32("1550")
    },
    created_at: ISODate("2026-01-24T16:00:00.000Z"),
    plan_id: "100001323",
    user_id: Long("6"),
    is_favorite: true,
    updated_at: ISODate("2026-01-24T03:39:27.063Z"),
    status: "\"todo\""
} ]);

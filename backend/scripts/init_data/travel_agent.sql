/*
 Navicat Premium Dump SQL

 Source Server         : 43.138.139.21-mysql
 Source Server Type    : MySQL
 Source Server Version : 80045 (8.0.45)
 Source Host           : 43.138.139.21:3306
 Source Schema         : travel_agent

 Target Server Type    : MySQL
 Target Server Version : 80045 (8.0.45)
 File Encoding         : 65001

 Date: 04/03/2026 11:25:05
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for audit_logs
-- ----------------------------
DROP TABLE IF EXISTS `audit_logs`;
CREATE TABLE `audit_logs`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NULL DEFAULT NULL COMMENT '操作用户ID，NULL表示系统操作',
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '用户名（冗余，避免JOIN）',
  `action` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型',
  `resource` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作资源',
  `resource_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '资源ID',
  `details` json NULL COMMENT '操作详情',
  `ip_address` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'IP地址',
  `user_agent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT 'User-Agent',
  `method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT 'HTTP方法 (GET/POST/PUT/DELETE)',
  `path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '请求路径 (/api/user/123)',
  `status_code` smallint NULL DEFAULT NULL COMMENT 'HTTP响应状态码',
  `duration_ms` int NULL DEFAULT NULL COMMENT '请求耗时(ms)',
  `response_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '响应结果 (success/error)',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_action`(`user_id` ASC, `action` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_method_path`(`method` ASC, `path` ASC) USING BTREE,
  INDEX `idx_status_code`(`status_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 29 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '审计日志表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of audit_logs
-- ----------------------------
INSERT INTO `audit_logs` VALUES (1, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"logs\": [], \"total\": 0}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/logs/audit', 200, 117, 'success', '2026-03-04 10:30:39');
INSERT INTO `audit_logs` VALUES (2, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 1, \"comments\": [{\"content\": \"11\", \"post_id\": \"post_BuZl1QC4qPM4V1tKBNe7YA\", \"user_id\": 5007, \"parent_id\": null, \"comment_id\": \"comment_OZhAby1aDIjOyY_n\", \"created_at\": \"2026-03-03T06:18:36.408000\", \"like_count\": 0}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/comments', 200, 124, 'success', '2026-03-04 10:30:47');
INSERT INTO `audit_logs` VALUES (3, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"posts\": [{\"tags\": [\"旅行\", \"长城\"], \"title\": \"北京一日游11\", \"content\": \"今天去了长城，风景真美！\", \"post_id\": \"696eee0b9a79c062f8cccc4e\", \"user_id\": 5007, \"created_at\": \"2026-03-02T10:52:59.309000\", \"like_count\": 11, \"media_urls\": [\"https://img95.699pic.com/photo/50136/6765.jpg_wh860.jpg\"], \"updated_at\": \"2026-03-02T10:52:59.309000\", \"view_count\": 100.0, \"comment_count\": 2, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"故宫\"], \"title\": \"故宫旅行\", \"content\": \"在故宫里拍了很多照片，历史感十足！\", \"post_id\": \"696eee0b9a79c062f8cccc4f\", \"user_id\": 7, \"created_at\": \"2026-03-01T22:52:59.309000\", \"like_count\": 16, \"media_urls\": [\"https://bpic.588ku.com/back_origin_min_pic/19/09/23/593eae9555db91d7908839deecd452da.jpg\"], \"updated_at\": \"2026-03-02T22:52:59.309000\", \"view_count\": 89.0, \"comment_count\": 0, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"西湖\"], \"title\": \"西湖观赏\", \"content\": \"西湖的美景让人流连忘返！\", \"post_id\": \"696eee0b9a79c062f8cccc50\", \"user_id\": 5007, \"created_at\": \"2026-02-28T04:52:59\", \"like_count\": 9, \"media_urls\": [\"https://youimg1.c-ctrip.com/target/100d14000000vu15e552D_D_10000_1200.jpg?proc=autoorient\"], \"updated_at\": \"2026-03-01T04:52:59\", \"view_count\": 78.0, \"comment_count\": 4, \"moderation_status\": \"pending\"}], \"total\": 3}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/posts/moderation', 200, 53, 'success', '2026-03-04 10:31:31');
INSERT INTO `audit_logs` VALUES (4, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"logs\": [{\"id\": 3, \"path\": \"/api/admin/posts/moderation\", \"action\": \"查询\", \"method\": \"GET\", \"details\": {\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"posts\": [{\"tags\": [\"旅行\", \"长城\"], \"title\": \"北京一日游11\", \"content\": \"今天去了长城，风景真美！\", \"post_id\": \"696eee0b9a79c062f8cccc4e\", \"user_id\": 5007, \"created_at\": \"2026-03-02T10:52:59.309000\", \"like_count\": 11, \"media_urls\": [\"https://img95.699pic.com/photo/50136/6765.jpg_wh860.jpg\"], \"updated_at\": \"2026-03-02T10:52:59.309000\", \"view_count\": 100.0, \"comment_count\": 2, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"故宫\"], \"title\": \"故宫旅行\", \"content\": \"在故宫里拍了很多照片，历史感十足！\", \"post_id\": \"696eee0b9a79c062f8cccc4f\", \"user_id\": 7, \"created_at\": \"2026-03-01T22:52:59.309000\", \"like_count\": 16, \"media_urls\": [\"https://bpic.588ku.com/back_origin_min_pic/19/09/23/593eae9555db91d7908839deecd452da.jpg\"], \"updated_at\": \"2026-03-02T22:52:59.309000\", \"view_count\": 89.0, \"comment_count\": 0, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"西湖\"], \"title\": \"西湖观赏\", \"content\": \"西湖的美景让人流连忘返！\", \"post_id\": \"696eee0b9a79c062f8cccc50\", \"user_id\": 5007, \"created_at\": \"2026-02-28T04:52:59\", \"like_count\": 9, \"media_urls\": [\"https://youimg1.c-ctrip.com/target/100d14000000vu15e552D_D_10000_1200.jpg?proc=autoorient\"], \"updated_at\": \"2026-03-01T04:52:59\", \"view_count\": 78.0, \"comment_count\": 4, \"moderation_status\": \"pending\"}], \"total\": 3}}}, \"user_id\": 10000, \"resource\": \"admin\", \"username\": \"admin\", \"created_at\": \"2026-03-04T10:31:31\", \"ip_address\": \"183.17.228.70\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0\", \"duration_ms\": 53, \"resource_id\": null, \"status_code\": 200, \"response_status\": \"success\"}, {\"id\": 2, \"path\": \"/api/admin/comments\", \"action\": \"查询\", \"method\": \"GET\", \"details\": {\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 1, \"comments\": [{\"content\": \"11\", \"post_id\": \"post_BuZl1QC4qPM4V1tKBNe7YA\", \"user_id\": 5007, \"parent_id\": null, \"comment_id\": \"comment_OZhAby1aDIjOyY_n\", \"created_at\": \"2026-03-03T06:18:36.408000\", \"like_count\": 0}]}}}, \"user_id\": 10000, \"resource\": \"admin\", \"username\": \"admin\", \"created_at\": \"2026-03-04T10:30:47\", \"ip_address\": \"183.17.228.70\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0\", \"duration_ms\": 124, \"resource_id\": null, \"status_code\": 200, \"response_status\": \"success\"}, {\"id\": 1, \"path\": \"/api/admin/logs/audit\", \"action\": \"查询\", \"method\": \"GET\", \"details\": {\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"logs\": [], \"total\": 0}}}, \"user_id\": 10000, \"resource\": \"admin\", \"username\": \"admin\", \"created_at\": \"2026-03-04T10:30:39\", \"ip_address\": \"183.17.228.70\", \"user_agent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0\", \"duration_ms\": 117, \"resource_id\": null, \"status_code\": 200, \"response_status\": \"success\"}], \"total\": 3}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/logs/audit', 200, 111, 'success', '2026-03-04 10:34:37');
INSERT INTO `audit_logs` VALUES (5, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 3, \"users\": [{\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\", \"feishu_open_id\": \"\", \"feishu_union_id\": \"\"}, {\"id\": 5007, \"role\": \"user\", \"email\": \"ccc@tencent.com\", \"username\": \"周新杰\", \"is_active\": true, \"avatar_url\": \"https://s1-imfile.feishucdn.com/static-resource/v1/v3_00uk_1701c4db-67ae-456a-8fa8-2d23061f117g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp\", \"created_at\": \"2026-03-03T02:21:36\", \"is_verified\": true, \"last_login_at\": \"2026-03-03T17:48:43\", \"feishu_open_id\": \"ou_74311939bd55a1d9934bd014005b4496\", \"feishu_union_id\": \"on_6896fcd6e46719f349771480d6f7460d\"}, {\"id\": 7, \"role\": \"user\", \"email\": \"test_1@example.com\", \"username\": \"user1\", \"is_active\": true, \"avatar_url\": null, \"created_at\": \"2026-02-27T14:48:27\", \"is_verified\": false, \"last_login_at\": \"2026-03-02T09:59:30\", \"feishu_open_id\": null, \"feishu_union_id\": null}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/users', 200, 113, 'success', '2026-03-04 10:36:43');
INSERT INTO `audit_logs` VALUES (6, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"posts\": [{\"tags\": [\"旅行\", \"长城\"], \"title\": \"北京一日游11\", \"content\": \"今天去了长城，风景真美！\", \"post_id\": \"696eee0b9a79c062f8cccc4e\", \"user_id\": 5007, \"created_at\": \"2026-03-02T10:52:59.309000\", \"like_count\": 11, \"media_urls\": [\"https://img95.699pic.com/photo/50136/6765.jpg_wh860.jpg\"], \"updated_at\": \"2026-03-02T10:52:59.309000\", \"view_count\": 100.0, \"comment_count\": 2, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"故宫\"], \"title\": \"故宫旅行\", \"content\": \"在故宫里拍了很多照片，历史感十足！\", \"post_id\": \"696eee0b9a79c062f8cccc4f\", \"user_id\": 7, \"created_at\": \"2026-03-01T22:52:59.309000\", \"like_count\": 16, \"media_urls\": [\"https://bpic.588ku.com/back_origin_min_pic/19/09/23/593eae9555db91d7908839deecd452da.jpg\"], \"updated_at\": \"2026-03-02T22:52:59.309000\", \"view_count\": 89.0, \"comment_count\": 0, \"moderation_status\": \"pending\"}, {\"tags\": [\"旅行\", \"西湖\"], \"title\": \"西湖观赏\", \"content\": \"西湖的美景让人流连忘返！\", \"post_id\": \"696eee0b9a79c062f8cccc50\", \"user_id\": 5007, \"created_at\": \"2026-02-28T04:52:59\", \"like_count\": 9, \"media_urls\": [\"https://youimg1.c-ctrip.com/target/100d14000000vu15e552D_D_10000_1200.jpg?proc=autoorient\"], \"updated_at\": \"2026-03-01T04:52:59\", \"view_count\": 78.0, \"comment_count\": 4, \"moderation_status\": \"pending\"}], \"total\": 3}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/posts/moderation', 200, 60, 'success', '2026-03-04 10:38:42');
INSERT INTO `audit_logs` VALUES (7, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 76, 'success', '2026-03-04 10:48:14');
INSERT INTO `audit_logs` VALUES (8, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 37, 'success', '2026-03-04 10:48:27');
INSERT INTO `audit_logs` VALUES (9, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 3, \"users\": [{\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\", \"feishu_open_id\": \"\", \"feishu_union_id\": \"\"}, {\"id\": 5007, \"role\": \"user\", \"email\": \"ccc@tencent.com\", \"username\": \"周新杰\", \"is_active\": true, \"avatar_url\": \"https://s1-imfile.feishucdn.com/static-resource/v1/v3_00uk_1701c4db-67ae-456a-8fa8-2d23061f117g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp\", \"created_at\": \"2026-03-03T02:21:36\", \"is_verified\": true, \"last_login_at\": \"2026-03-03T17:48:43\", \"feishu_open_id\": \"ou_74311939bd55a1d9934bd014005b4496\", \"feishu_union_id\": \"on_6896fcd6e46719f349771480d6f7460d\"}, {\"id\": 7, \"role\": \"user\", \"email\": \"test_1@example.com\", \"username\": \"user1\", \"is_active\": true, \"avatar_url\": null, \"created_at\": \"2026-02-27T14:48:27\", \"is_verified\": false, \"last_login_at\": \"2026-03-02T09:59:30\", \"feishu_open_id\": null, \"feishu_union_id\": null}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/users', 200, 78, 'success', '2026-03-04 10:48:48');
INSERT INTO `audit_logs` VALUES (10, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 1, \"comments\": [{\"content\": \"11\", \"post_id\": \"post_BuZl1QC4qPM4V1tKBNe7YA\", \"user_id\": 5007, \"parent_id\": null, \"comment_id\": \"comment_OZhAby1aDIjOyY_n\", \"created_at\": \"2026-03-03T06:18:36.408000\", \"like_count\": 0}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/comments', 200, 59, 'success', '2026-03-04 10:48:50');
INSERT INTO `audit_logs` VALUES (11, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 45, 'success', '2026-03-04 10:48:58');
INSERT INTO `audit_logs` VALUES (12, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 69, 'success', '2026-03-04 10:50:58');
INSERT INTO `audit_logs` VALUES (13, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 42, 'success', '2026-03-04 10:52:02');
INSERT INTO `audit_logs` VALUES (14, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 49, 'success', '2026-03-04 10:52:16');
INSERT INTO `audit_logs` VALUES (15, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 41, 'success', '2026-03-04 10:52:35');
INSERT INTO `audit_logs` VALUES (16, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 48, 'success', '2026-03-04 10:54:09');
INSERT INTO `audit_logs` VALUES (17, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 41, 'success', '2026-03-04 10:54:45');
INSERT INTO `audit_logs` VALUES (18, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 3, \"users\": [{\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\", \"feishu_open_id\": \"\", \"feishu_union_id\": \"\"}, {\"id\": 5007, \"role\": \"user\", \"email\": \"ccc@tencent.com\", \"username\": \"周新杰\", \"is_active\": true, \"avatar_url\": \"https://s1-imfile.feishucdn.com/static-resource/v1/v3_00uk_1701c4db-67ae-456a-8fa8-2d23061f117g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp\", \"created_at\": \"2026-03-03T02:21:36\", \"is_verified\": true, \"last_login_at\": \"2026-03-03T17:48:43\", \"feishu_open_id\": \"ou_74311939bd55a1d9934bd014005b4496\", \"feishu_union_id\": \"on_6896fcd6e46719f349771480d6f7460d\"}, {\"id\": 7, \"role\": \"user\", \"email\": \"test_1@example.com\", \"username\": \"user1\", \"is_active\": true, \"avatar_url\": null, \"created_at\": \"2026-02-27T14:48:27\", \"is_verified\": false, \"last_login_at\": \"2026-03-02T09:59:30\", \"feishu_open_id\": null, \"feishu_union_id\": null}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/users', 200, 91, 'success', '2026-03-04 10:54:59');
INSERT INTO `audit_logs` VALUES (19, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 44, 'success', '2026-03-04 10:55:46');
INSERT INTO `audit_logs` VALUES (20, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 40, 'success', '2026-03-04 10:56:02');
INSERT INTO `audit_logs` VALUES (21, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 3, \"users\": [{\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\", \"feishu_open_id\": \"\", \"feishu_union_id\": \"\"}, {\"id\": 5007, \"role\": \"user\", \"email\": \"ccc@tencent.com\", \"username\": \"周新杰\", \"is_active\": true, \"avatar_url\": \"https://s1-imfile.feishucdn.com/static-resource/v1/v3_00uk_1701c4db-67ae-456a-8fa8-2d23061f117g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp\", \"created_at\": \"2026-03-03T02:21:36\", \"is_verified\": true, \"last_login_at\": \"2026-03-03T17:48:43\", \"feishu_open_id\": \"ou_74311939bd55a1d9934bd014005b4496\", \"feishu_union_id\": \"on_6896fcd6e46719f349771480d6f7460d\"}, {\"id\": 7, \"role\": \"user\", \"email\": \"test_1@example.com\", \"username\": \"user1\", \"is_active\": true, \"avatar_url\": null, \"created_at\": \"2026-02-27T14:48:27\", \"is_verified\": false, \"last_login_at\": \"2026-03-02T09:59:30\", \"feishu_open_id\": null, \"feishu_union_id\": null}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/users', 200, 82, 'success', '2026-03-04 11:00:06');
INSERT INTO `audit_logs` VALUES (22, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 3, \"users\": [{\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\", \"feishu_open_id\": \"\", \"feishu_union_id\": \"\"}, {\"id\": 5007, \"role\": \"user\", \"email\": \"ccc@tencent.com\", \"username\": \"周新杰\", \"is_active\": true, \"avatar_url\": \"https://s1-imfile.feishucdn.com/static-resource/v1/v3_00uk_1701c4db-67ae-456a-8fa8-2d23061f117g~?image_size=72x72&cut_type=&quality=&format=image&sticker_format=.webp\", \"created_at\": \"2026-03-03T02:21:36\", \"is_verified\": true, \"last_login_at\": \"2026-03-03T17:48:43\", \"feishu_open_id\": \"ou_74311939bd55a1d9934bd014005b4496\", \"feishu_union_id\": \"on_6896fcd6e46719f349771480d6f7460d\"}, {\"id\": 7, \"role\": \"user\", \"email\": \"test_1@example.com\", \"username\": \"user1\", \"is_active\": true, \"avatar_url\": null, \"created_at\": \"2026-02-27T14:48:27\", \"is_verified\": false, \"last_login_at\": \"2026-03-02T09:59:30\", \"feishu_open_id\": null, \"feishu_union_id\": null}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/users', 200, 19379, 'success', '2026-03-04 11:08:47');
INSERT INTO `audit_logs` VALUES (23, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"total\": 1, \"comments\": [{\"content\": \"11\", \"post_id\": \"post_BuZl1QC4qPM4V1tKBNe7YA\", \"user_id\": 5007, \"parent_id\": null, \"comment_id\": \"comment_OZhAby1aDIjOyY_n\", \"created_at\": \"2026-03-03T06:18:36.408000\", \"like_count\": 0}]}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/comments', 200, 101, 'success', '2026-03-04 11:08:47');
INSERT INTO `audit_logs` VALUES (24, 10000, 'admin', '查询', 'admin', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": \"[响应数据过大，已截断，原始长度 27517 字节]\"}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/admin/logs/audit', 200, 229, 'success', '2026-03-04 11:08:47');
INSERT INTO `audit_logs` VALUES (25, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 38515, 'success', '2026-03-04 11:20:32');
INSERT INTO `audit_logs` VALUES (26, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 41, 'success', '2026-03-04 11:20:32');
INSERT INTO `audit_logs` VALUES (27, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 48, 'success', '2026-03-04 11:20:47');
INSERT INTO `audit_logs` VALUES (28, 10000, 'admin', '查询', 'user', NULL, '{\"response\": {\"msg\": \"获取成功\", \"code\": 200, \"data\": {\"id\": 10000, \"role\": \"admin\", \"email\": \"admin@123.com\", \"profile\": {\"travel_stats\": {}, \"visited_cities\": [], \"travel_preferences\": []}, \"username\": \"admin\", \"is_active\": true, \"avatar_url\": \"https://java-webai-1.oss-cn-beijing.aliyuncs.com/travel_avatars/avatar_6_vzOwiuvh2eA.jpg\", \"created_at\": \"2026-03-03T10:55:19\", \"is_verified\": false, \"last_login_at\": \"2026-03-03T17:50:40\"}}}', '183.17.228.70', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0', 'GET', '/api/user/profile', 200, 49, 'success', '2026-03-04 11:21:45');

-- ----------------------------
-- Table structure for captcha_records
-- ----------------------------
DROP TABLE IF EXISTS `captcha_records`;
CREATE TABLE `captcha_records`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `session_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '会话ID',
  `captcha_code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '验证码',
  `attempt_count` int NOT NULL DEFAULT 0 COMMENT '尝试次数',
  `is_verified` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否已验证',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `expires_at` timestamp NOT NULL COMMENT '过期时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_session`(`session_id` ASC) USING BTREE,
  INDEX `idx_expires`(`expires_at` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '验证码记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of captcha_records
-- ----------------------------

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '权限名称',
  `resource` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'API资源',
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '操作类型: create, read, update, delete',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '权限描述',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  UNIQUE INDEX `unique_permission`(`resource` ASC, `action` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 25 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '权限表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES (1, '查看个人资料', 'user', 'read', '查看自己的用户资料', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (2, '编辑个人资料', 'user', 'update', '编辑自己的用户资料', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (3, '修改密码', 'user', 'update_password', '修改自己的密码', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (4, '生成旅行计划', 'trip', 'create', '生成新的旅行计划', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (5, '查看旅行计划', 'trip', 'read', '查看自己的旅行计划', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (6, '编辑旅行计划', 'trip', 'update', '编辑自己的旅行计划', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (7, '删除旅行计划', 'trip', 'delete', '删除自己的旅行计划', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (8, '创建对话', 'dialog', 'create', '创建对话会话', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (9, '查看对话历史', 'dialog', 'read', '查看自己的对话历史', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (10, '删除对话', 'dialog', 'delete', '删除自己的对话', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (11, '发布帖子', 'post', 'create', '发布新帖子', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (12, '查看帖子', 'post', 'read', '查看帖子', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (13, '编辑帖子', 'post', 'update', '编辑自己的帖子', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (14, '删除帖子', 'post', 'delete', '删除自己的帖子', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (15, '发表评论', 'comment', 'create', '发表评论', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (16, '删除评论', 'comment', 'delete', '删除自己的评论', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (17, '点赞', 'like', 'create', '点赞帖子或评论', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (18, '取消点赞', 'like', 'delete', '取消点赞', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (19, '关注用户', 'follow', 'create', '关注其他用户', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (20, '取消关注', 'follow', 'delete', '取消关注用户', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (21, '管理用户', 'admin_user', 'manage', '管理所有用户', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (22, '审核内容', 'admin_content', 'moderate', '审核用户发布的内容', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (23, '查看系统日志', 'admin_log', 'read', '查看系统日志', '2026-01-15 10:14:30');
INSERT INTO `permissions` VALUES (24, '系统配置', 'admin_config', 'manage', '管理系统配置', '2026-01-15 10:14:30');

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions`  (
  `role_id` int NOT NULL COMMENT '角色ID',
  `permission_id` int NOT NULL COMMENT '权限ID',
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `permission_id`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '角色权限关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of role_permissions
-- ----------------------------
INSERT INTO `role_permissions` VALUES (1, 1);
INSERT INTO `role_permissions` VALUES (2, 1);
INSERT INTO `role_permissions` VALUES (1, 2);
INSERT INTO `role_permissions` VALUES (2, 2);
INSERT INTO `role_permissions` VALUES (1, 3);
INSERT INTO `role_permissions` VALUES (2, 3);
INSERT INTO `role_permissions` VALUES (1, 4);
INSERT INTO `role_permissions` VALUES (2, 4);
INSERT INTO `role_permissions` VALUES (1, 5);
INSERT INTO `role_permissions` VALUES (2, 5);
INSERT INTO `role_permissions` VALUES (1, 6);
INSERT INTO `role_permissions` VALUES (2, 6);
INSERT INTO `role_permissions` VALUES (1, 7);
INSERT INTO `role_permissions` VALUES (2, 7);
INSERT INTO `role_permissions` VALUES (1, 8);
INSERT INTO `role_permissions` VALUES (2, 8);
INSERT INTO `role_permissions` VALUES (1, 9);
INSERT INTO `role_permissions` VALUES (2, 9);
INSERT INTO `role_permissions` VALUES (1, 10);
INSERT INTO `role_permissions` VALUES (2, 10);
INSERT INTO `role_permissions` VALUES (1, 11);
INSERT INTO `role_permissions` VALUES (2, 11);
INSERT INTO `role_permissions` VALUES (1, 12);
INSERT INTO `role_permissions` VALUES (2, 12);
INSERT INTO `role_permissions` VALUES (1, 13);
INSERT INTO `role_permissions` VALUES (2, 13);
INSERT INTO `role_permissions` VALUES (1, 14);
INSERT INTO `role_permissions` VALUES (2, 14);
INSERT INTO `role_permissions` VALUES (1, 15);
INSERT INTO `role_permissions` VALUES (2, 15);
INSERT INTO `role_permissions` VALUES (1, 16);
INSERT INTO `role_permissions` VALUES (2, 16);
INSERT INTO `role_permissions` VALUES (1, 17);
INSERT INTO `role_permissions` VALUES (2, 17);
INSERT INTO `role_permissions` VALUES (1, 18);
INSERT INTO `role_permissions` VALUES (2, 18);
INSERT INTO `role_permissions` VALUES (1, 19);
INSERT INTO `role_permissions` VALUES (2, 19);
INSERT INTO `role_permissions` VALUES (1, 20);
INSERT INTO `role_permissions` VALUES (2, 20);
INSERT INTO `role_permissions` VALUES (2, 21);
INSERT INTO `role_permissions` VALUES (2, 22);
INSERT INTO `role_permissions` VALUES (2, 23);
INSERT INTO `role_permissions` VALUES (2, 24);

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '角色名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '角色描述',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '角色表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, 'user', '普通用户角色', '2026-01-15 10:14:30');
INSERT INTO `roles` VALUES (2, 'admin', '管理员角色，拥有所有权限', '2026-01-15 10:14:30');

-- ----------------------------
-- Table structure for tags
-- ----------------------------
DROP TABLE IF EXISTS `tags`;
CREATE TABLE `tags`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '标签名称',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '标签分类',
  `use_count` int NOT NULL DEFAULT 0 COMMENT '使用次数',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  INDEX `idx_category`(`category` ASC) USING BTREE,
  INDEX `idx_use_count`(`use_count` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '标签表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of tags
-- ----------------------------
INSERT INTO `tags` VALUES (1, '美食', '美食类', 0, '2026-01-20 11:04:24');
INSERT INTO `tags` VALUES (2, '风景', '风景类', 0, '2026-01-20 11:04:35');
INSERT INTO `tags` VALUES (3, '日出', '日出类', 0, '2026-02-07 15:11:33');
INSERT INTO `tags` VALUES (4, '极光', NULL, 0, '2026-02-09 13:35:22');
INSERT INTO `tags` VALUES (5, '自然景象', NULL, 0, '2026-02-09 13:35:22');


-- ----------------------------
-- Table structure for user_profiles
-- ----------------------------
DROP TABLE IF EXISTS `user_profiles`;
CREATE TABLE `user_profiles`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `gender` enum('male','female','other') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '性别',
  `birth_date` date NULL DEFAULT NULL COMMENT '出生日期',
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '所在地',
  `travel_preferences` json NULL COMMENT '旅行偏好标签数组',
  `visited_cities` json NULL COMMENT '访问过的城市数组',
  `travel_stats` json NULL COMMENT '旅行统计信息',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `full_name`(`full_name` ASC) USING BTREE,
  CONSTRAINT `user_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户档案表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_profiles
-- ----------------------------
INSERT INTO `user_profiles` VALUES (3, 5007, '周新杰', 'male', '2026-03-04', '深圳', '[\"nickname:杰\", \"bio:很懒\", \"location:深圳\"]', '[\"北京\", \"上海\", \"重庆\", \"广州\", \"深圳\", \"珠海\", \"汕头\", \"汕尾\", \"杭州\", \"南京\", \"厦门\", \"福州\", \"龙岩\", \"兰州\", \"海口\", \"呼和浩特\"]', '{\"total_trips\": 1, \"total_cities\": 1, \"favorite_trips\": 1, \"completed_trips\": 0}', '2026-03-03 02:21:36', '2026-03-04 02:51:56');

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles`  (
  `user_id` bigint NOT NULL COMMENT '用户ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户角色关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user_roles
-- ----------------------------
INSERT INTO `user_roles` VALUES (7, 1);
INSERT INTO `user_roles` VALUES (5007, 1);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '邮箱',
  `password_hash` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '密码哈希，飞书用户可为空',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '手机号',
  `avatar_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '头像URL',
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '个人简介',
  `role` enum('user','admin') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user' COMMENT '用户角色',
  `is_active` tinyint(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
  `is_verified` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否验证邮箱',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login_at` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `feishu_open_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '飞书用户 open_id',
  `feishu_union_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '飞书用户 union_id',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `feishu_open_id`(`feishu_open_id` ASC) USING BTREE,
  UNIQUE INDEX `feishu_union_id`(`feishu_union_id` ASC) USING BTREE,
  INDEX `idx_username`(`username` ASC) USING BTREE,
  INDEX `idx_email`(`email` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE,
  INDEX `idx_feishu_open_id`(`feishu_open_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10001 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of users (超级管理员-默认密码123456**）
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', '', '$2a$10$OKU4EkkNZMbV/vo5XQ3I4.yKdCgwgvu3u6thPvpLZ7UAliXT56Cpi', '', 'https://java-webai-1.oss-cn-https://vcg03.cfp.cn/creative/vcg/800/new/VCG211522516989.jpg', '我是管理员', 'admin', 1, 0, '2026-03-03 10:55:19', '2026-03-04 03:14:06', '2026-03-03 17:50:40', '', '');

SET FOREIGN_KEY_CHECKS = 1;

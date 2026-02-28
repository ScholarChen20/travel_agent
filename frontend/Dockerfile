# 前端构建镜像
FROM node:18-alpine AS build

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源码
COPY . .

# 赋予vite执行权限
RUN chmod +x ./node_modules/.bin/vite

# 构建生产版本
RUN ./node_modules/.bin/vite build

# Nginx镜像
FROM nginx:1.25-alpine

# 复制构建产物到Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
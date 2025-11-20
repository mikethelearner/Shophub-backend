# 🚀 Free Deployment Guide - ShopHub E-Commerce Platform

This guide will help you deploy your ShopHub E-Commerce Platform **100% FREE** using:
- **Backend**: Render (Free tier)
- **Frontend**: Vercel (Free tier)
- **Database**: MongoDB Atlas (Free tier - 512MB)
- **Images**: Cloudinary (Free tier - 10GB)

---

## 📋 Prerequisites

Before starting, create free accounts on these platforms:

1. **GitHub Account** - [github.com](https://github.com)
2. **Render Account** - [render.com](https://render.com)
3. **Vercel Account** - [vercel.com](https://vercel.com)
4. **MongoDB Atlas** - [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
5. **Cloudinary** - [cloudinary.com](https://cloudinary.com)

---

## 🗄️ Step 1: Setup MongoDB Atlas (Database)

### 1.1 Create MongoDB Atlas Account
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Click **"Try Free"** and sign up
3. Choose **"Free Shared"** tier (M0)

### 1.2 Create a Cluster
1. After login, click **"Build a Database"**
2. Select **"M0 FREE"** tier
3. Choose a cloud provider (AWS recommended) and region (closest to you)
4. Click **"Create"**

### 1.3 Create Database User
1. Click **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Username: `shophub_user` (or your choice)
5. Password: Generate a strong password and **SAVE IT**
6. Database User Privileges: **"Read and write to any database"**
7. Click **"Add User"**

### 1.4 Whitelist IP Addresses
1. Click **"Network Access"** in left sidebar
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Click **"Confirm"**

### 1.5 Get Connection String
1. Click **"Database"** in left sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Copy the connection string (looks like):
   ```
   mongodb+srv://shophub_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add database name at the end: `mongodb+srv://shophub_user:yourpassword@cluster0.xxxxx.mongodb.net/ecommerce?retryWrites=true&w=majority`
7. **SAVE THIS CONNECTION STRING** - you'll need it for Render

---

## 🖼️ Step 2: Setup Cloudinary (Image Storage)

### 2.1 Create Cloudinary Account
1. Go to [cloudinary.com](https://cloudinary.com)
2. Click **"Sign Up for Free"**
3. Complete registration

### 2.2 Get API Credentials
1. After login, go to **Dashboard**
2. You'll see:
   - **Cloud Name**
   - **API Key**
   - **API Secret**
3. **SAVE THESE CREDENTIALS** - you'll need them for Render

---

## 📤 Step 3: Push Code to GitHub

### 3.1 Initialize Git Repository (if not already done)
```bash
cd "/home/techwarrior/Programming-And-Development/Projects/personal projects/ShopHub-E-Commerce-Platform"
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

### 3.2 Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click **"+"** → **"New repository"**
3. Name: `shophub-ecommerce`
4. Keep it **Public** (required for free Render deployment)
5. Click **"Create repository"**

### 3.3 Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/shophub-ecommerce.git
git branch -M main
git push -u origin main
```

---

## 🔧 Step 4: Deploy Backend to Render

### 4.1 Create New Web Service
1. Go to [render.com](https://render.com) and login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your **shophub-ecommerce** repository

### 4.2 Configure Web Service
Fill in the following:

| Field | Value |
|-------|-------|
| **Name** | `shophub-backend` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `./build.sh` |
| **Start Command** | `gunicorn ecommerce.wsgi:application` |
| **Instance Type** | **Free** |

### 4.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"** and add these:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.10.0` | Python version |
| `SECRET_KEY` | Click "Generate" | Django secret key |
| `DEBUG` | `False` | Production mode |
| `ALLOWED_HOSTS` | `.onrender.com` | Will update after deployment |
| `MONGODB_URI` | Your MongoDB connection string | From Step 1.5 |
| `CLOUDINARY_CLOUD_NAME` | Your cloud name | From Step 2.2 |
| `CLOUDINARY_API_KEY` | Your API key | From Step 2.2 |
| `CLOUDINARY_API_SECRET` | Your API secret | From Step 2.2 |

### 4.4 Deploy
1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://shophub-backend.onrender.com`

### 4.5 Update ALLOWED_HOSTS
1. Go to your service → **"Environment"**
2. Update `ALLOWED_HOSTS` to: `shophub-backend.onrender.com,localhost,127.0.0.1`
3. Service will automatically redeploy

### 4.6 Test Backend
Visit: `https://shophub-backend.onrender.com/admin`
- You should see the Django admin login page
- Login with: `admin@gmail.com` / `admin123`

---

## 🌐 Step 5: Deploy Frontend to Vercel

### 5.1 Update Frontend API URL
1. Open `frontend/.env.production`
2. Update with your Render backend URL:
   ```
   VITE_API_URL=https://shophub-backend.onrender.com/api
   ```
3. Commit and push:
   ```bash
   git add frontend/.env.production
   git commit -m "Update production API URL"
   git push
   ```

### 5.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and login
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 5.3 Add Environment Variable
1. Go to **"Environment Variables"**
2. Add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://shophub-backend.onrender.com/api`
   - **Environment**: All (Production, Preview, Development)

### 5.4 Deploy
1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. You'll get a URL like: `https://shophub-ecommerce.vercel.app`

---

## ✅ Step 6: Test Your Deployment

### 6.1 Test Frontend
1. Visit your Vercel URL
2. Browse products
3. Add items to cart
4. Create an account / Login

### 6.2 Test Checkout & WhatsApp
1. Add products to cart
2. Go to checkout
3. Fill in shipping information
4. Place order
5. You should be redirected to WhatsApp with order details!

### 6.3 Test Admin Panel
1. Visit: `https://shophub-backend.onrender.com/admin`
2. Login with: `admin@gmail.com` / `admin123`
3. Add a new product
4. Upload an image (will be stored in Cloudinary)
5. Check if the product appears on your frontend

---

## 🎯 Important Notes

### ⚠️ Render Free Tier Limitations
- **Cold Starts**: Service sleeps after 15 minutes of inactivity
- **First request after sleep**: Takes 30-60 seconds to wake up
- **Solution**: Use a service like [UptimeRobot](https://uptimerobot.com) (free) to ping your backend every 14 minutes

### 💾 Data Persistence
- ✅ **Database (MongoDB Atlas)**: Permanent storage
- ✅ **Images (Cloudinary)**: Permanent storage
- ❌ **Render filesystem**: Temporary (resets on redeploy)

### 🔒 Security
- Change default admin password after first login
- Keep your environment variables secret
- Never commit `.env` files to GitHub

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Build fails on Render
- **Solution**: Check build logs, ensure `build.sh` has execute permissions

**Problem**: Database connection error
- **Solution**: Verify MongoDB connection string, check IP whitelist

**Problem**: Images not uploading
- **Solution**: Verify Cloudinary credentials in environment variables

### Frontend Issues

**Problem**: Can't connect to backend
- **Solution**: Check `VITE_API_URL` in Vercel environment variables

**Problem**: 404 errors on page refresh
- **Solution**: Ensure `vercel.json` has correct rewrites configuration

### General Issues

**Problem**: Slow first load
- **Solution**: This is normal for Render free tier (cold start)

**Problem**: Products not showing
- **Solution**: Add products via admin panel, check browser console for errors

---

## 🎉 Congratulations!

Your ShopHub E-Commerce Platform is now live and **100% FREE**!

### Your URLs:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.onrender.com`
- **Admin Panel**: `https://your-backend.onrender.com/admin`

### Next Steps:
1. Add your products via admin panel
2. Customize the WhatsApp message if needed
3. Share your store link with customers!

---

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Review Render/Vercel deployment logs
3. Check browser console for frontend errors
4. Verify all environment variables are set correctly

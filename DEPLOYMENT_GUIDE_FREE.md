# Free Backend Deployment Guide (Render + MongoDB Atlas + Cloudinary)

This guide will help you deploy your Django backend for **free**. Since Render filesystems are ephemeral (deleted after restart) and don't provide a built-in database on the free tier, we will use:
1.  **Render**: For hosting the Django application (Compute).
2.  **MongoDB Atlas**: For the database (Data).
3.  **Cloudinary**: For product images and media files (Media).

---

## Step 1: Set up MongoDB Atlas (Database)

1.  Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up/login.
2.  **Create a Cluster**:
    *   Click **+ Create**.
    *   Select **M0 Sandbox** (Free Tier).
    *   Choose a provider (AWS) and region (closest to you).
    *   Click **Create Deployment**.
3.  **Create a Database User**:
    *   Go to **Security** -> **Database Access**.
    *   Click **+ Add New Database User**.
    *   Method: **Password**.
    *   Username: `shophub_admin` (or your choice).
    *   Password: **Generate a strong password and save it**.
    *   Role: **Read and write to any database**.
    *   Click **Add User**.
4.  **Allow Network Access**:
    *   Go to **Security** -> **Network Access**.
    *   Click **+ Add IP Address**.
    *   Select **Allow Access from Anywhere** (`0.0.0.0/0`). (Required for Render to connect).
    *   Click **Confirm**.
5.  **Get Connection String**:
    *   Go to **Deployment** -> **Database** -> Click **Connect** on your cluster.
    *   Select **Drivers**.
    *   Copy the connection string (e.g., `mongodb+srv://shophub_admin:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority`).
    *   **IMPORTANT**: Replace `<password>` with the password you created in step 3. Keep this URL safe; this is your `MONGODB_URI`.

---

## Step 2: Set up Cloudinary (Images)

1.  Go to [Cloudinary](https://cloudinary.com/) and sign up for a free account.
2.  Go to your **Dashboard**.
3.  Copy the following values:
    *   **Cloud Name**
    *   **API Key**
    *   **API Secret**

---

## Step 3: Configure Render (Hosting)

1.  Push your latest changes to GitHub (including the `render.yaml` update I just made).
2.  Go to the [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** and select **Blueprint**.
4.  Connect your GitHub repository `Shophub-backend`.
5.  Render will detect the `render.yaml` file and ask for Environment Variables. Enter the values you prepared:

    *   `PYTHON_VERSION`: `3.10.0` (Default)
    *   `SECRET_KEY`: (Click "Generate" or enter a random string)
    *   `DEBUG`: `False`
    *   `ALLOWED_HOSTS`: `*` (or your frontend domain later)
    *   `MONGODB_URI`: Paste your MongoDB Atlas connection string from Step 1.
    *   `CLOUDINARY_CLOUD_NAME`: Your Cloud Name from Step 2.
    *   `CLOUDINARY_API_KEY`: Your API Key from Step 2.
    *   `CLOUDINARY_API_SECRET`: Your API Secret from Step 2.

6.  Click **Apply**.
7.  Render will start building your app. Watch the logs.
    *   It will install dependencies.
    *   It will run `build.sh` (collectstatic, migrations, create superuser).
    *   **Success**: You should see "Your service is live".

---

## Step 4: Verify & Connect Frontend

1.  Copy your backend URL from the Render dashboard (e.g., `https://shophub-backend.onrender.com`).
2.  **Update your specific API Endpoint**: Open a browser and go to `https://shophub-backend.onrender.com/api/products/` (or your health check endpoint) to confirm it's running.
3.  **Update Frontend**: Go to your Frontend code/repo.
    *   Find where you define the backend URL (usually a `.env` file or a `config.js`).
    *   Change `http://localhost:8000` to your new Render URL.
    *   Redeploy your Frontend Vercel project.

## Troubleshooting
- **Build Failed?** Check the logs. If it says "directory not found", ensure `rootDir: backend` is in `render.yaml`.
- **Database Error?** Check your `MONGODB_URI`. Ensure you replaced `<password>` and that IP Access is set to `0.0.0.0/0` in Atlas.
- **Images not uploading?** Check your Cloudinary credentials.

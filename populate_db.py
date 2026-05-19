import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy import delete, select, update

import models
from config import settings
from database import AsyncSessionLocal, engine
from image_utils import _get_s3_client
from main import app

POPULATE_IMAGES_DIR = Path("populate_images")

USERS = [
    {
        "username": "SamKajeiy",
        "email": "mwangisam20020@gmail.com",
        "password": "TestPassword1!",
        "image": "kanairo.jpg",
    },
    {
        "username": "JubiTheGoat",
        "email": "jubi@test.com",
        "password": "TestPassword2!",
        "image": "jubi.jpg",
    },
    {
        "username": "DrakeMinion",
        "email": "drake@test.com",
        "password": "TestPassword3!",
        "image": "drake.png",
    },
    {
        "username": "NairobiCoder",
        "email": "kaimusdavis@gmail.com",
        "password": "TestPassword4!",
        "image": "altman10.png",
    },
    {
        "username": "TechWithAisha",
        "email": "aisha@test.com",
        "password": "TestPassword5!",
        "image": "aisha.jpg",
    },
    {
        "username": "BackendBrian",
        "email": "brian@test.com",
        "password": "TestPassword6!",
        "image": "sam.jpg",
    },
    {
        "username": "CloudQueen",
        "email": "cloudqueen@test.com",
        "password": "TestPassword7!",
        "image": "babyelphant.png",
    },
    {
        "username": "DockerDave",
        "email": "dave@test.com",
        "password": "TestPassword8!",
        "image": "Eminem.jpg",
    },
    {
        "username": "PostgressPro",
        "email": "postgres@test.com",
        "password": "TestPassword9!",
        "image": "hack.png",
    },
    {
        "username": "OpenSourceOliver",
        "email": "oliver@test.com",
        "password": "TestPassword10!",
        "image": "boga.jpg",
    },
]

POSTS = [
    {
        "title": "Why FastAPI is the Future of Python APIs",
        "content": "I spent years building APIs with Flask and Django REST Framework. When I finally tried FastAPI, everything changed. The automatic docs, type hints, and blazing speed make it my go-to framework. If you haven't tried it yet, drop everything and start today.",
    },
    {
        "title": "My First Week Learning Python",
        "content": "The first week learning Python felt like learning a new language — because it literally was. But unlike French class in high school, this one actually stuck. Indentation was the first thing that broke my brain. Coming from JavaScript, I kept adding curly braces out of habit.",
    },
    {
        "title": "SQLAlchemy 2.0 — Worth the Learning Curve",
        "content": "If you're still using SQLAlchemy 1.x patterns, I get it — change is hard. But 2.0's new style with select() and mapped_column() is so much cleaner. Once it clicks, you'll never want to go back. Pair it with async and you have a seriously powerful setup.",
    },
    {
        "title": "Building in Public Changed My Career",
        "content": "Six months ago I started pushing every project to GitHub and posting about what I was learning on LinkedIn. The response was unexpected. People started reaching out, offering advice, sharing resources. Building in public is the cheat code nobody tells you about.",
    },
    {
        "title": "Docker Finally Makes Sense",
        "content": "I avoided Docker for two years because it seemed complicated. Then one day a senior dev sat with me for 20 minutes and walked me through it. Containers are just isolated environments. That's it. Now I Dockerize everything and I can't imagine going back.",
    },
    {
        "title": "PostgreSQL vs SQLite — When to Use Which",
        "content": "SQLite is perfect for development and small projects. Zero setup, file-based, fast. PostgreSQL is what you want in production — robust, concurrent, full-featured. Use SQLite to move fast, switch to PostgreSQL before you go live. FastAPI handles both beautifully.",
    },
    {
        "title": "The Moment Async Programming Clicked",
        "content": "I read about async/await for months before it actually clicked. Then someone explained it like this: imagine a chef who puts water on to boil and instead of standing there watching it, goes and chops vegetables. That's async. One thread, multiple things happening. Game changer.",
    },
    {
        "title": "Pydantic is My Favourite Python Library",
        "content": "Define a class with type hints, and Pydantic handles validation, serialization, and documentation automatically. No more writing if statements to check if a field exists. No more try-except blocks around type casting. Just clean, validated data every time.",
    },
    {
        "title": "Git Commit Messages Actually Matter",
        "content": "I used to write commit messages like 'fix', 'update', 'changes'. Then I joined a team project and had to read other people's commit history. Now I write messages like 'fix: resolve 404 error on login route' and 'feat: add JWT authentication'. Future me says thank you.",
    },
    {
        "title": "How I Passed My First Technical Interview",
        "content": "I bombed my first three technical interviews. The fourth one I passed. The difference? I stopped trying to memorize solutions and started learning patterns. Two pointers, sliding window, hash maps. Once you know the patterns, the problems become recognizable.",
    },
    {
        "title": "REST APIs in Plain English",
        "content": "A REST API is just a waiter. You tell it what you want (request), it goes to the kitchen (server), and brings back your food (response). GET means bring me something. POST means create something new. PUT means update something. DELETE means remove it. That's really all there is to it.",
    },
    {
        "title": "Why I Started Learning Backend Development",
        "content": "I started with frontend — HTML, CSS, JavaScript. It was fun but I always wondered what happened when you clicked submit on a form. Where did the data go? How did it come back? That curiosity pulled me into backend. Now I can build both sides and it feels like a superpower.",
    },
    {
        "title": "JWT Authentication Explained Simply",
        "content": "A JWT is like a signed wristband at a concert. The venue (server) gives it to you when you pay (login). Every time you want to get into a section (protected route), you show the wristband. The staff (server) checks the signature, not a database. Fast, stateless, elegant.",
    },
    {
        "title": "The Best Free Resources for Learning Python",
        "content": "Python.org official docs — underrated and thorough. Real Python — excellent in-depth tutorials. CS50P from Harvard — completely free and world class. Automate the Boring Stuff — practical and fun. YouTube channels like Corey Schafer and Tech With Tim. All free. No excuses.",
    },
    {
        "title": "Dependency Injection Doesn't Have to Be Scary",
        "content": "When I first heard 'dependency injection' I thought it was some advanced enterprise Java thing. In FastAPI it's just passing things your function needs as parameters. Need a database session? Add it as a parameter with Depends(). Need the current user? Same thing. Clean and simple.",
    },
    {
        "title": "My Honest Review of VS Code",
        "content": "VS Code wins on extensions. There's an extension for everything — Python linting, Git integration, database viewers, REST clients. The IntelliSense is sharp, it's fast, and it's free. I've tried PyCharm and Neovim. I always come back to VS Code. It just works.",
    },
    {
        "title": "How Nairobi's Tech Scene Surprised Me",
        "content": "Before I got into tech I didn't realize how vibrant Nairobi's developer community was. There are meetups, hackathons, boot camps, and communities everywhere. iHub, Moringa, Andela — these places are producing world-class engineers. If you're in Kenya and want to get into tech, the ecosystem is there.",
    },
    {
        "title": "Understanding HTTP Status Codes Once and for All",
        "content": "2xx means success. 200 OK. 201 Created. 204 No Content. 3xx means redirect. 4xx means the client did something wrong. 400 Bad Request. 401 Unauthorized. 403 Forbidden. 404 Not Found. 422 Validation Error. 5xx means the server messed up. 500 Internal Server Error. Memorize these.",
    },
    {
        "title": "Why I Use UV Instead of pip",
        "content": "pip works. UV is just faster. Dramatically faster. Installing packages that used to take 30 seconds now take 2. It also handles virtual environments cleanly. Once you switch you'll wonder how you ever tolerated pip's speed. It's built in Rust which explains everything.",
    },
    {
        "title": "The Power of Environment Variables",
        "content": "Never hardcode a password, API key, or secret in your code. Not even once. Not even in a private repo. Use environment variables. Use a .env file. Add .env to .gitignore immediately. Use pydantic-settings to load them cleanly in FastAPI. This is not optional — it's Security 101.",
    },
    {
        "title": "Cloud Computing for Absolute Beginners",
        "content": "The cloud is just someone else's computer. AWS, GCP, Azure — they're all just massive data centers you can rent compute from. EC2 is a virtual machine. S3 is file storage. RDS is a managed database. Lambda is code that runs without a server. Start with one service and expand from there.",
    },
    {
        "title": "What Nobody Tells You About Being a Junior Developer",
        "content": "You will Google things every single day. Senior developers Google things every single day. The skill isn't memorizing syntax — it's knowing what to search for, how to read documentation, and how to debug efficiently. Stack Overflow, GitHub issues, and official docs are your best friends.",
    },
    {
        "title": "CORS Errors and How to Actually Fix Them",
        "content": "CORS errors feel personal. Like the browser is personally rejecting you. But it's just a security feature. Your frontend and backend are on different origins, so the browser blocks the request. In FastAPI, add CORSMiddleware with your allowed origins. In production, be specific. Never use '*' in production.",
    },
    {
        "title": "Async vs Sync Routes in FastAPI — Which to Use",
        "content": "Use async def when you're doing I/O — database calls, HTTP requests, file reads. Use def for CPU-bound work or when using sync libraries. FastAPI handles both gracefully. Mixing them incorrectly is where performance problems creep in. When in doubt, async def with await is the right call.",
    },
    {
        "title": "The Day I Understood Decorators",
        "content": "Python decorators confused me for months. Then I realized — a decorator is just a function that wraps another function. @app.get('/') is just FastAPI's way of saying 'register this function as a GET handler for this path'. Once that clicked, decorators went from magic to just... Python.",
    },
    {
        "title": "Freelancing as a Developer in Africa",
        "content": "Upwork, Fiverr, Toptal — the platforms exist. The competition is global. The advantage of being based in Africa is that your cost of living is lower, meaning you can price competitively and still earn well relative to your market. Build a strong portfolio, get a few reviews, and compound from there.",
    },
    {
        "title": "My Favourite Programming Quotes",
        "content": "'Make it work, make it right, make it fast' — Kent Beck. 'Programs must be written for people to read, and only incidentally for machines to execute' — Harold Abelson. 'The best code is no code at all' — Jeff Atwood. These three quotes guide how I write code every day.",
    },
    {
        "title": "Routers in FastAPI — Keeping Code Clean",
        "content": "Putting every route in main.py works until it doesn't. Once you have 20+ endpoints, that file becomes chaos. FastAPI's APIRouter lets you split routes into separate files by feature — users.py, posts.py, auth.py — and include them cleanly in main.py. Do this from day one.",
    },
    {
        "title": "How to Read a Stack Trace",
        "content": "When your code breaks, read the error from the bottom up. The last line tells you what went wrong. Scan upward for YOUR file — ignore the library code. Go to that exact line. Read the error message slowly — it almost always tells you exactly what to fix. Most bugs are solved in under 5 minutes this way.",
    },
    {
        "title": "Hashing Passwords — Why You Never Store Plain Text",
        "content": "Storing passwords in plain text is one of the worst things you can do as a developer. If your database is ever compromised, every user's password is exposed. Use bcrypt or passlib to hash passwords before storing. The hash is one-way — you can verify but never reverse. This is non-negotiable.",
    },
    {
        "title": "Open Source Contribution — Where to Start",
        "content": "Find a project you actually use. Read the contributing guide. Look for issues tagged 'good first issue'. Fix a typo in the docs. Add a missing test. Submit a small PR. Get feedback. Iterate. Your first contribution doesn't need to be impressive — it just needs to be real.",
    },
    {
        "title": "What I Wish I Knew Before Learning to Code",
        "content": "I wish someone told me that confusion is the process, not a sign you're failing. That copying code without understanding it is the slowest way to learn. That building something broken and fixing it teaches more than any tutorial. And that consistency — even 30 minutes a day — compounds into expertise.",
    },
    {
        "title": "Postman vs curl — Pick Your Weapon",
        "content": "Both test APIs. Postman gives you a GUI — great for exploring and saving requests. curl is terminal-based — great for scripting and automation. I use Postman when building, curl when scripting. FastAPI's built-in Swagger UI is actually excellent for quick testing too. Use all three.",
    },
    {
        "title": "Why Python's simplicity is Deceptive",
        "content": "Python looks easy because the syntax is clean. But mastering Python — decorators, generators, context managers, async, metaclasses — takes years. The barrier to entry is low. The ceiling is incredibly high. Don't mistake readable syntax for a simple language. Python rewards the curious.",
    },
    {
        "title": "Response Models Are Your Security Layer",
        "content": "Your database model might have a password_hash field. Your response model should absolutely not. Define what goes out using response_model in your FastAPI route and Pydantic will filter everything else out automatically. This is the easiest security win in FastAPI. Use it always.",
    },
    {
        "title": "The Importance of Naming Things Well",
        "content": "get_user vs fetch_user_data_from_database_by_id_and_return — one of these is good naming. Variables, functions, and files should say what they do without needing a comment. If you need a comment to explain what a variable is, rename the variable. Good naming is a form of documentation.",
    },
    {
        "title": "Testing Your API — Why Bother",
        "content": "Because future you will thank present you. Write tests for your endpoints. FastAPI's TestClient makes it straightforward. Test the happy path. Test edge cases. Test what happens with invalid input. A test suite lets you refactor confidently without wondering if you broke something.",
    },
    {
        "title": "Background Tasks — Don't Make Users Wait",
        "content": "User submits a form, your API sends a confirmation email. Don't make them wait for the email to send before returning a response. Use FastAPI's BackgroundTasks to fire off the email after returning 200. Instant response, email sends in the background. Users are happy. Everyone wins.",
    },
    {
        "title": "The Art of Writing Good Commit Messages",
        "content": "Use the imperative mood: 'Add login route' not 'Added login route'. Keep the subject under 50 characters. Reference issue numbers when relevant. A good commit message tells the story of why, not just what. Your git log should read like a changelog, not a mystery novel.",
    },
    {
        "title": "My Experience at Moringa School",
        "content": "Moringa School was intense. Nine months of full-stack development, built on top of the pressure of daily projects, peer reviews, and technical assessments. What it gave me was a foundation — Python, JavaScript, React, REST APIs, databases, Git. And a network of developers building things across East Africa.",
    },
    {
        "title": "Why Documentation is a Developer's Best Friend",
        "content": "I used to skip documentation and go straight to Stack Overflow. Bad habit. Official docs are written by the people who built the thing. FastAPI's docs are exceptional — clear, example-heavy, and comprehensive. Read them. Then read them again. You'll find things you missed every time.",
    },
    {
        "title": "Understanding Middleware in FastAPI",
        "content": "Middleware sits between every request and your route handlers. It runs before and after. Use it for logging, authentication checks, adding response headers, rate limiting, CORS. It's one of those features that seems advanced until you use it, and then you wonder how you lived without it.",
    },
    {
        "title": "The Difference Between Authentication and Authorization",
        "content": "Authentication is proving who you are — logging in with username and password. Authorization is proving what you're allowed to do — can you delete this post or only your own? JWT handles authentication. Your route logic handles authorization. Both matter. Don't confuse them.",
    },
    {
        "title": "Pagination — Don't Return Everything at Once",
        "content": "Returning 10,000 records in a single API response is a performance disaster. Implement pagination. limit and offset is the simplest approach. Cursor-based pagination is better for large datasets. FastAPI makes both easy to implement. Your database, server, and users will all thank you.",
    },
    {
        "title": "Lessons From Debugging for 6 Hours",
        "content": "Last week I spent 6 hours debugging an issue that turned out to be a missing comma in a dictionary. SIX HOURS. The lesson: take breaks. Fresh eyes catch what tired eyes miss. Rubber duck debug — explain the problem out loud. And read error messages slowly. They almost always point to the answer.",
    },
    {
        "title": "Why Every Developer Should Learn SQL",
        "content": "ORMs are great until they're not. When you need to optimize a slow query, understand what your ORM is generating, or write a complex join, SQL knowledge saves you. Learn SELECT, WHERE, JOIN, GROUP BY, and indexes. These fundamentals never go out of style regardless of what ORM you use.",
    },
    {
        "title": "Containerizing a FastAPI App with Docker",
        "content": "Write a Dockerfile. FROM python:3.12-slim. COPY requirements. RUN pip install. COPY your app. CMD uvicorn. Build the image. Run the container. Deploy anywhere. That's the beauty of Docker — consistency across every environment. Works on my machine AND in production. Finally.",
    },
    {
        "title": "Rate Limiting — Protect Your API",
        "content": "Without rate limiting, one bad actor can bring down your API with a flood of requests. Implement rate limiting — restrict requests per IP, per user, or per endpoint. Return 429 Too Many Requests when the limit is hit. It's one of those things you don't think about until you need it desperately.",
    },
    {
        "title": "The Compounding Effect of Learning Every Day",
        "content": "30 minutes of learning every day sounds modest. But that's 182 hours in a year. 182 hours of focused Python, FastAPI, SQL, Docker, cloud. That's the equivalent of multiple university courses. Compound interest applies to skills too. Start small. Stay consistent. The results will shock you.",
    },
    {
        "title": "What Building Real Projects Taught Me That Tutorials Never Could",
        "content": "Tutorials show you the happy path. Real projects show you everything else. The cryptic error at 2am. The dependency that breaks everything. The feature that seemed simple but wasn't. The refactor that touched 15 files. Real projects are frustrating and messy and slow — and they're where real learning happens.",
    },
    {
        "title": "GraphQL vs REST — My Honest Take",
        "content": "REST is battle-tested, simple, and well understood. GraphQL is flexible and powerful for complex data needs. For most projects — especially starting out — REST is the right choice. Learn it deeply first. GraphQL solves real problems, but problems you probably don't have yet. Master the fundamentals first.",
    },
]

POST_51 = {
    "title": "Fun Fact: I Once Debugged a Bug for 3 Days That Was Just a Typo",
    "content": "If you've paginated all the way to this post — the 51st one — you deserve to know this: I once spent three full days hunting a bug that turned out to be a variable named 'recieve' instead of 'receive'. Three days. The compiler didn't catch it. My eyes didn't catch it. A fresh pair of eyes caught it in 30 seconds. Always get a second pair of eyes. Always.",
}


async def clear_existing_data() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.User.image_file))
        image_files = [
            image_file for image_file in result.scalars().all() if image_file
        ]

        s3 = _get_s3_client()
        for image_file in image_files:
            key = f"profile_pics/{image_file}"
            try:
                s3.delete_object(Bucket=settings.s3_bucket_name, Key=key)
            except (BotoCoreError, ClientError) as err:
                print(f"Could not delete profile picture from S3: {image_file} ({err})")

        await db.execute(delete(models.Post))
        await db.execute(delete(models.User))
        await db.commit()
    print("Cleared existing data")


async def update_post_dates() -> None:
    now = datetime.now(UTC)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(models.Post).order_by(models.Post.id))
        posts = result.scalars().all()

        if not posts:
            return

        # First post (POST_51) is the oldest - ~90 days ago
        await db.execute(
            update(models.Post)
            .where(models.Post.id == posts[0].id)
            .values(date_posted=now - timedelta(days=90)),
        )

        # Remaining posts: each ~1.5 days newer than previous
        for i, post in enumerate(posts[1:], start=1):
            days_ago = (len(posts) - i) * 1.5
            hours_offset = (i * 7) % 24
            post_date = now - timedelta(days=days_ago, hours=hours_offset)
            await db.execute(
                update(models.Post)
                .where(models.Post.id == post.id)
                .values(date_posted=post_date),
            )

        await db.commit()
    print("Updated post dates")


async def populate() -> None:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://localhost",
    ) as client:
        # Clear existing data (local images first, then database)
        await clear_existing_data()

        users: list[dict] = []

        print(f"\nCreating {len(USERS)} users...")
        for user_data in USERS:  # FIX 3: entire block is inside this loop
            response = await client.post(
                "/api/users",
                json={
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            user = response.json()
            print(f"  Created: {user['username']}")

            response = await client.post(
                "/api/users/token",
                data={
                    "username": user_data["email"],
                    "password": user_data["password"],
                },
            )
            response.raise_for_status()
            token = response.json()["access_token"]

            if image_name := user_data.get("image"):
                if image_name.startswith("http"):
                    # FIX 1: removed `import httpx` from here
                    # FIX 2: reuse existing `client` instead of httpx.AsyncClient()
                    avatar_response = await client.get(image_name)
                    avatar_response.raise_for_status()
                    response = await client.patch(
                        f"/api/users/{user['id']}/picture",
                        files={
                            "file": (
                                "avatar.svg",
                                avatar_response.content,
                                "image/svg+xml",
                            ),
                        },
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    response.raise_for_status()
                    print(f"    Uploaded avatar from URL: {image_name}")
                else:
                    # Handle local file
                    image_path = POPULATE_IMAGES_DIR / image_name
                    if image_path.exists():
                        response = await client.patch(
                            f"/api/users/{user['id']}/picture",
                            files={
                                "file": (
                                    image_name,
                                    image_path.read_bytes(),
                                    "image/png",
                                ),
                            },
                            headers={"Authorization": f"Bearer {token}"},
                        )
                        response.raise_for_status()
                        print(f"    Uploaded: {image_name}")

            users.append(  # FIX 3: also inside the loop now
                {"id": user["id"], "username": user["username"], "token": token},
            )

        print(f"\nCreating {len(POSTS) + 1} posts...")

        # First create POST_51 (will become oldest after date update)
        response = await client.post(
            "/api/posts",
            json={"title": POST_51["title"], "content": POST_51["content"]},
            headers={"Authorization": f"Bearer {users[0]['token']}"},
        )
        response.raise_for_status()
        print(f"  Created: '{POST_51['title']}'")

        # Create remaining posts in reverse (last in list = oldest, first = newest)
        for i, post_data in enumerate(reversed(POSTS)):
            user = users[i % len(users)]
            response = await client.post(
                "/api/posts",
                json={
                    "title": post_data["title"],
                    "content": post_data["content"],
                },
                headers={"Authorization": f"Bearer {user['token']}"},
            )
            response.raise_for_status()
            title = post_data["title"]
            print(
                (
                    f"  Created: '{title[:50]}...'"
                    if len(title) > 50
                    else f"  Created: '{title}'"
                ),
            )

        print("\nUpdating post dates...")
        await update_post_dates()

    await engine.dispose()

    print("\nDone!")
    print(f"  {len(USERS)} users")
    print(f"  {len(POSTS) + 1} posts")
    print("  Profile pictures saved locally")


if __name__ == "__main__":
    asyncio.run(populate())

# New Features Guide

> Comprehensive documentation for the latest features added to Job & Scholarship Tracker

**Version:** 1.1.0
**Last Updated:** November 6, 2025
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Notes System](#notes-system)
3. [Tag System](#tag-system)
4. [Archive Functionality](#archive-functionality)
5. [Interview Management](#interview-management)
6. [Referral Tracking](#referral-tracking)
7. [Enhanced Analytics](#enhanced-analytics)
8. [Advanced Filtering](#advanced-filtering)
9. [API Endpoints](#api-endpoints)
10. [Tips & Best Practices](#tips--best-practices)

---

## 🎯 Overview

This release introduces powerful new features to help you organize, track, and analyze your job and scholarship applications more effectively. These features have been designed with simplicity and productivity in mind.

### What's New

- **📝 Rich Text Notes** - Create detailed, formatted notes with auto-save
- **🏷️ Custom Tags** - Organize applications with color-coded tags
- **📦 Archive System** - Clean up your dashboard without deleting applications
- **🎤 Interview Management** - Schedule and track interviews with interviewer details
- **👥 Referral Tracking** - Keep track of who referred you and when
- **📊 Analytics Dashboard** - Visualize your application flow with interactive charts
- **🔍 Advanced Filtering** - Multi-select filters with date ranges and saved presets
- **⚡ Quick Actions** - AJAX-powered operations for faster workflow

---

## 📝 Notes System

The Notes System allows you to create rich-text notes that can be linked to specific applications or kept as standalone entries.

### Key Features

- **Rich Text Editor** powered by Quill.js
- **Auto-save** functionality (saves every 3 seconds)
- **Pin Important Notes** to the top of your list
- **Link to Applications** or keep as general notes
- **Full-text Search** across all your notes
- **Markdown-style Formatting** with headings, lists, bold, italic, links

### How to Create a Note

1. **Navigate to Notes**
   - Click **"Notes"** in the main navigation menu
   - Or click **"Add Note"** from the dashboard

2. **Create Your Note**
   - Enter a title (or leave as "Untitled Note")
   - Use the rich text editor to format your content:
     - **Bold** (Ctrl/Cmd + B)
     - *Italic* (Ctrl/Cmd + I)
     - Headings (H1, H2, H3)
     - Bulleted and numbered lists
     - Links and quotes
   - Optionally link to a specific application
   - Toggle "Pin to top" to keep it visible

3. **Auto-Save**
   - Notes are automatically saved every 3 seconds
   - You'll see "Saved" indicator when auto-save completes
   - No need to manually click save!

### Viewing and Managing Notes

**Notes List View**
- Access via **Notes** menu item
- See all your notes sorted by pinned status and update time
- Pinned notes appear at the top with a 📌 icon
- Search notes by title or content

**Edit a Note**
- Click on any note to edit it
- Changes are auto-saved
- Toggle pin status anytime

**Delete a Note**
- Click the delete button (trash icon)
- Confirm deletion (this action is permanent)

### Use Cases

- **Interview Preparation**: Create notes for each interview with talking points and company research
- **Application Insights**: Document specific details about applications (compensation, benefits, team info)
- **Follow-up Tracking**: Keep track of conversations with recruiters and next steps
- **General Reference**: Store tips, templates, and resources you frequently use

### Pro Tips

✅ **Pin your most important notes** (interview prep, follow-up templates) for quick access
✅ **Use headings** to structure longer notes for easy scanning
✅ **Link notes to applications** to keep all related information in one place
✅ **Search functionality** makes finding specific information fast

---

## 🏷️ Tag System

Tags help you categorize and filter applications with custom labels and colors.

### Key Features

- **Custom Tag Names** - Create any tag you need
- **Color Coding** - Choose from any color to visually identify tags
- **Multiple Tags per Application** - Assign as many tags as needed
- **Tag-based Filtering** - Quickly find applications by tag
- **Tag Count** - See how many applications use each tag
- **User-specific** - Your tags are private to your account

### Common Tag Examples

**Job Type Tags:**
- 🏠 Remote
- 🏢 On-site
- 🌐 Hybrid
- 📍 Relocation Required

**Application Stage Tags:**
- 🔥 Hot Lead
- ⏰ Urgent
- 🎯 Dream Company
- 💰 High Salary
- 🌟 Great Culture

**Skill-based Tags:**
- 💻 Full Stack
- 🤖 AI/ML
- ☁️ Cloud
- 📊 Data Science
- 🎨 Design

**Strategy Tags:**
- 🥇 Top Priority
- 🧪 Practice Interview
- 📞 Phone Screen
- 👔 Final Round

### How to Create Tags

**Method 1: Via Application Form**
1. Create or edit an application
2. Look for the **Tags** section
3. Click **"+ Create New Tag"**
4. Enter tag name and choose a color
5. Click **"Create Tag"**

**Method 2: Via Tag Management**
1. Go to **Settings** → **Tags** (coming soon)
2. Click **"Create New Tag"**
3. Enter name and pick a color
4. Save

### Assigning Tags to Applications

1. **While Creating/Editing an Application:**
   - In the application form, find the Tags field
   - Select one or more tags from the dropdown
   - Tags are saved with the application

2. **Tag Filtering:**
   - On the dashboard, use the filter panel
   - Select tags to show only applications with those tags
   - Combine with other filters for precise results

### Managing Tags

**View Tag Usage:**
- Each tag shows how many applications use it
- Empty tags can be deleted without affecting applications

**Edit Tag:**
- Change tag name or color anytime
- All applications using the tag are automatically updated

**Delete Tag:**
- Deleting a tag removes it from all applications
- Applications themselves are not affected

### Color Recommendations

- **Green** (#10b981) - Positive/Success (e.g., "High Match", "Good Fit")
- **Red** (#ef4444) - Urgent/Important (e.g., "Urgent", "Hot Lead")
- **Blue** (#3b82f6) - Professional/Corporate (e.g., "Enterprise", "F500")
- **Purple** (#8b5cf6) - Creative/Tech (e.g., "Startup", "Innovative")
- **Yellow** (#f59e0b) - Attention (e.g., "Follow Up", "Waiting")
- **Gray** (#6b7280) - Neutral (e.g., "Research", "Maybe")

### Best Practices

✅ **Create a consistent tagging system** from the start
✅ **Use 3-5 tags per application** to avoid over-tagging
✅ **Color-code by category** (all location tags use one color, all priority tags use another)
✅ **Review and clean up unused tags** periodically
✅ **Combine tags with filters** for powerful search capabilities

---

## 📦 Archive Functionality

Archive completed or old applications to keep your dashboard clean without losing data.

### When to Archive vs. Delete

**Archive When:**
- ✅ Application process is complete (accepted, rejected, withdrawn)
- ✅ Application is no longer active but you want to keep records
- ✅ You want to reduce dashboard clutter
- ✅ You might need to reference the application later
- ✅ You want to preserve application history

**Delete When:**
- ❌ Application was created by mistake
- ❌ Application is a duplicate
- ❌ You'll never need the data again
- ❌ Data contains errors you can't fix

### How to Archive Applications

**Single Application:**
1. Open the application detail page
2. Click **"Archive"** button (archive box icon)
3. Application is moved to archive immediately
4. You'll see a confirmation message

**From Dashboard:**
1. Find the application you want to archive
2. Click the three-dot menu (⋯)
3. Select **"Archive"**
4. Confirm if prompted

**Bulk Archive (Multiple Applications):**
1. On the dashboard, select multiple applications using checkboxes
2. Click **"Bulk Actions"** → **"Archive Selected"**
3. All selected applications are archived at once
4. Confirmation shows how many were archived

### Viewing Archived Applications

1. Click **"Archive"** in the navigation menu
2. View all your archived applications
3. Search archived applications using the search bar
4. See when each application was archived

### Restoring from Archive

1. Go to **Archive** page
2. Find the application you want to restore
3. Click **"Restore"** button
4. Application returns to your main dashboard
5. All data, notes, and tags are preserved

### Archive Features

- **Preserves All Data**: Questions, responses, notes, interviews, referrals remain intact
- **Searchable**: Search archived applications by title, company, or description
- **Archived Date**: See when each application was archived
- **Easy Restoration**: One-click restore to active applications
- **Separate View**: Archived apps don't clutter your dashboard

### Best Practices

✅ **Archive rejected applications** after recording any feedback
✅ **Archive accepted applications** you didn't choose
✅ **Archive old applications** from previous job searches
✅ **Keep archive organized** by reviewing and deleting truly unnecessary items periodically
✅ **Don't archive applications with upcoming deadlines** or active interviews

---

## 🎤 Interview Management

Track interviews, manage interviewer information, and prepare effectively.

### Key Features

- **Interview Scheduling** with date, time, and duration
- **Interview Types**: Phone, Video, On-site, Panel
- **Interviewer Details**: Name, title, contact info, LinkedIn profile
- **Meeting Links**: Store Zoom/Teams/Google Meet links
- **Interview Status**: Scheduled, Completed, Cancelled, Rescheduled
- **Interview Notes**: Preparation notes, topics to cover, feedback
- **Multiple Interviewers**: Add multiple interviewers per interview

### Interview Types

- **📞 Phone Interview**: Traditional phone screening or interview
- **🎥 Video Interview**: Zoom, Teams, Google Meet, etc.
- **🏢 On-site Interview**: In-person at company location
- **👥 Panel Interview**: Multiple interviewers at once

### How to Schedule an Interview

**Method 1: From Application Detail Page**

1. Open the application
2. Scroll to **Interviews** section
3. Click **"Schedule Interview"**
4. Fill in interview details:
   - **Type**: Select from Phone, Video, On-site, Panel
   - **Date & Time**: Use the datetime picker
   - **Duration**: Enter duration in minutes (default: 60)
   - **Location**: Physical address for on-site interviews
   - **Meeting Link**: Video call link for virtual interviews
   - **Notes**: Preparation notes, topics, agenda
   - **Status**: Usually "Scheduled" for new interviews

5. **Add Interviewers** (optional but recommended):
   - Click **"Add Interviewer"**
   - Enter:
     - Full name
     - Job title
     - Email address
     - Phone number (optional)
     - LinkedIn URL (optional)
     - Notes (background research, prep notes)
   - Add multiple interviewers using "+ Add Another Interviewer"

6. Click **"Save Interview"**

**Method 2: Quick Interview (Dashboard)**

1. From dashboard, click the calendar icon next to an application
2. Quick modal appears
3. Enter basic details:
   - Interview type
   - Date and time
   - Meeting link (optional)
4. Click **"Schedule"**
5. Edit later to add more details

### Managing Interviews

**View All Interviews:**
1. Click **"Interviews"** in navigation menu
2. See calendar view with all upcoming and past interviews
3. Filter by status (Scheduled, Completed, Cancelled)

**Interview Details:**
- Interview type and datetime
- Duration
- Location or meeting link
- All interviewers with their contact info
- Your preparation notes
- Status indicator

**Edit Interview:**
1. Open the interview from application detail or interviews page
2. Click **"Edit"**
3. Update any details
4. Save changes

**Mark as Completed:**
1. Edit the interview
2. Change status to **"Completed"**
3. Add feedback notes
4. Save

**Cancel Interview:**
1. Edit the interview
2. Change status to **"Cancelled"**
3. Add reason in notes if desired
4. Save

**Delete Interview:**
- Use this only if interview was created by mistake
- Deleting is permanent (archiving the application preserves interviews)

### Interviewer Information

For each interviewer, you can store:

- **Name**: Full name of the interviewer
- **Title**: Their job title/position
- **Email**: Contact email
- **Phone**: Contact phone number
- **LinkedIn**: Their LinkedIn profile URL
- **Notes**: Research notes, background info, mutual connections

**Why Track Interviewer Details?**
- 📧 Send thank-you emails after the interview
- 🔍 Research their background on LinkedIn beforehand
- 💬 Personalize your conversation based on their role
- 📝 Remember specific topics they're interested in
- 🤝 Build relationships for future networking

### Interview Preparation Workflow

**1 Week Before:**
- [ ] Research the company thoroughly
- [ ] Study interviewer profiles on LinkedIn
- [ ] Prepare questions specific to each interviewer's role
- [ ] Review the job description
- [ ] Prepare your STAR stories

**1 Day Before:**
- [ ] Test your video setup (camera, microphone)
- [ ] Test the meeting link
- [ ] Prepare your environment (quiet space, good lighting)
- [ ] Review your notes
- [ ] Prepare questions to ask

**Day Of:**
- [ ] Join 5 minutes early for video interviews
- [ ] Have your resume and notes ready
- [ ] Have pen and paper for notes
- [ ] Stay calm and confident

**After Interview:**
- [ ] Add feedback notes immediately
- [ ] Send thank-you emails to all interviewers
- [ ] Mark interview as completed
- [ ] Update application status if needed

### Interview Notes Best Practices

**Before the Interview:**
```
PREPARATION NOTES
- Research: [Company mission, recent news, products]
- Interviewers: [Key info about each interviewer]
- Questions to Ask: [List your questions]
- Topics to Cover: [Your key selling points]
```

**During the Interview:**
```
INTERVIEW NOTES
- Key points discussed
- Interviewer's concerns or interests
- Next steps mentioned
- Important details about role/team
```

**After the Interview:**
```
POST-INTERVIEW FEEDBACK
- How I felt: [Your impression]
- What went well: [Positive moments]
- What to improve: [Areas for improvement]
- Follow-up needed: [Thank you emails, additional info]
- Overall assessment: [Good fit? Interest level?]
```

### Best Practices

✅ **Schedule interviews immediately** when you receive the invitation
✅ **Research all interviewers** on LinkedIn before the interview
✅ **Set reminders** 1 day and 1 hour before the interview
✅ **Test video links** at least 30 minutes before virtual interviews
✅ **Add detailed notes** about topics discussed and next steps
✅ **Send thank-you emails** within 24 hours of the interview
✅ **Update application status** to "Interview" when you schedule one

---

## 👥 Referral Tracking

Keep track of referrals and maintain relationships with people who help your job search.

### Key Features

- **Referrer Information**: Name, relationship, company, contact details
- **Referral Date**: When the referral was made
- **Notes**: Additional context about the referral
- **Application Link**: Automatically linked to the application
- **Contact Management**: Store email and phone for follow-ups

### Why Track Referrals?

- 📈 **Improve Success Rates**: Referred candidates have higher success rates
- 🙏 **Show Gratitude**: Thank your referrers appropriately
- 🤝 **Build Network**: Maintain relationships for future opportunities
- 📊 **Track ROI**: See which connections lead to interviews/offers
- 📝 **Follow-up**: Know when to update referrers on your progress

### How to Add a Referral

1. **Open the Application**
   - Navigate to the application detail page

2. **Add Referral Information**
   - Scroll to the **Referrals** section
   - Click **"Add Referral"**

3. **Fill in Referrer Details**:
   - **Name**: Full name of the person who referred you
   - **Relationship**: Your relationship to them
     - Examples: "Former colleague", "Friend", "Mentor", "LinkedIn connection", "College classmate"
   - **Company**: Where the referrer works
   - **Email**: Their contact email
   - **Phone**: Phone number (optional)
   - **Referral Date**: When they referred you
   - **Notes**: Any additional context
     - How you know them
     - What they said about the role
     - Follow-up commitments

4. **Save Referral**

### Relationship Examples

**Professional:**
- Former colleague
- Former manager
- Current colleague (different department)
- Mentor
- Industry contact
- Conference connection

**Personal:**
- Friend
- Family member
- College classmate
- Alumni connection
- Sports/hobby group member

**Network:**
- LinkedIn connection
- Twitter/social media contact
- Online community member
- Meetup group member
- Professional association member

### Managing Referrals

**View Referrals:**
- All referrals are shown on the application detail page
- See referrer name, company, and relationship at a glance

**Edit Referral:**
1. Click **"Edit"** next to the referral
2. Update any information
3. Save changes

**Delete Referral:**
- Only if added by mistake
- Deleting is permanent

### Follow-up Workflow

**After Submitting Application:**
1. Send thank-you message:
   ```
   Hi [Name],

   I wanted to thank you for referring me to [Position] at [Company].
   I submitted my application today and really appreciate your support!

   I'll keep you posted on how things progress.

   Thanks again,
   [Your name]
   ```

**After Interview:**
2. Update your referrer:
   ```
   Hi [Name],

   Quick update - I had my interview for [Position] yesterday.
   It went really well and I'm excited about the opportunity!

   Thanks again for making the connection.

   Best,
   [Your name]
   ```

**After Outcome:**
3. Share the result:
   - If **accepted**: Thank them and celebrate
   - If **rejected**: Thank them anyway and ask for feedback
   - Either way: Offer to return the favor

### Referral Notes Template

```
REFERRAL DETAILS
How we met: [Context of your relationship]
Strength of connection: [Close friend | Professional contact | Acquaintance]
Their role: [What they do at the company]
What they shared: [Insights about the role, team, or company]

FOLLOW-UP PLAN
- [ ] Thank you message sent (date: ___)
- [ ] Update after application submitted
- [ ] Update after interview
- [ ] Final outcome shared
- [ ] Return favor offer made

IMPORTANT NOTES
- [Any specific commitments or promises]
- [Timeline they mentioned]
- [Other connections they offered]
```

### Best Practices

✅ **Add referral info immediately** when you receive it
✅ **Send thank-you message** within 24 hours of the referral
✅ **Keep referrers updated** on major milestones
✅ **Be specific in your thanks** (mention what they did specifically)
✅ **Respect their time** (don't overburden with constant updates)
✅ **Return the favor** when you can help them or someone else
✅ **Maintain the relationship** beyond just the job application

---

## 📊 Enhanced Analytics

Visualize your application pipeline and track success metrics with interactive charts.

### Key Features

- **Sankey Flow Diagram**: See how applications move through stages
- **Timeline Visualization**: Upcoming deadlines and interviews
- **Summary Statistics**: Total apps, conversion rates, success metrics
- **Status Breakdown**: Applications by current status
- **Priority Distribution**: High/Medium/Low priority counts
- **Type Analysis**: Jobs vs. Scholarships
- **Time Filtering**: View data for 7, 30, or 60 days
- **Export Charts**: Download as PNG, SVG, or PDF

### Accessing Analytics

1. Click **"Analytics"** in the main navigation
2. Or click **"View Analytics"** from the dashboard
3. Analytics dashboard opens with all visualizations

### Summary Statistics

**Top Cards Show:**
- **Total Applications**: All-time application count
- **Job Applications**: Number of job applications
- **Scholarship Applications**: Number of scholarship applications
- **Success Rate**: Percentage of submitted applications that resulted in offers

**Key Metrics:**
- **Conversion Rate**: Offers ÷ Total Submitted × 100
- **Response Rate**: (Offers + Rejections) ÷ Total Submitted × 100
- **Average Time to Offer**: Coming soon
- **Interview Success Rate**: Coming soon

### Sankey Flow Diagram

**What It Shows:**
The Sankey diagram visualizes how your applications flow through different stages from start to finish.

**Understanding the Diagram:**
- **Nodes** (boxes): Each stage (Draft, Submitted, In Review, Interview, Offer, Rejected, Withdrawn)
- **Links** (flows): Applications moving from one stage to another
- **Width**: Thicker flows = more applications moved that way
- **Colors**: Each stage has a unique color for easy identification

**Stage Colors:**
- **Gray**: Draft
- **Blue**: Submitted
- **Amber**: In Review
- **Purple**: Interview
- **Green**: Offer (success!)
- **Red**: Rejected
- **Dark Gray**: Withdrawn

**How to Read It:**
1. Start from the left (Draft/Submitted)
2. Follow the flows to see common pathways
3. Wider flows indicate where most applications go
4. Identify bottlenecks (stages where applications get stuck)

**Example Insights:**
- "Most applications go from Submitted → In Review → Rejected"
  - **Action**: Improve application quality or targeting
- "Many applications go from Interview → Offer"
  - **Action**: Your interview skills are strong!
- "Few applications make it past Draft"
  - **Action**: Focus on completing and submitting applications

**Interactive Features:**
- **Hover**: See exact counts for each flow
- **Zoom**: Scroll to zoom in/out
- **Pan**: Click and drag to move the diagram

### Downloading Charts

**Sankey Diagram Download:**
1. Click **"Download Chart"** button above the Sankey diagram
2. Choose format:
   - **PNG**: Best for presentations and documents (high quality)
   - **SVG**: Best for editing in design software (vector)
   - **PDF**: Best for printing or archiving
3. Chart downloads automatically

**Use Cases:**
- Add to your portfolio
- Include in progress reports
- Share with career coaches or mentors
- Track long-term progress

### Timeline Visualization

**What It Shows:**
Upcoming deadlines and interviews chronologically.

**Features:**
- **Overdue items** highlighted in red
- **This week** items in yellow/warning
- **Future items** in normal colors
- **Interview vs. Deadline** icons distinguish event types

**Filtering Timeline:**
Use the dropdown to show:
- Next 7 days
- Next 14 days
- Next 30 days (default)
- Next 60 days
- Next 90 days

**Timeline Details:**
Each event shows:
- Application title and company
- Date and time
- Event type (interview or deadline)
- Application status
- Priority level
- Days until event

### Status Breakdown

**Visual Bar Chart Shows:**
- Draft: Applications not yet submitted
- Submitted: Applications sent but no response
- In Review: Applications being reviewed
- Interview: Interview scheduled or completed
- Offer: Received job/scholarship offer
- Rejected: Application rejected
- Withdrawn: You withdrew the application

**What to Look For:**
- **Too many drafts?** Focus on completing and submitting
- **Many in review?** Be patient, follow up after reasonable time
- **Low interview rate?** May need to improve application quality
- **High rejection rate?** Could be applying to roles that don't match

### Priority Distribution

**Shows:**
- **High Priority**: Applications marked as high priority
- **Medium Priority**: Standard priority
- **Low Priority**: Lower priority applications

**Pie Chart Visualization:**
- Red slice: High priority
- Yellow slice: Medium priority
- Green slice: Low priority

**Analysis:**
- Balance high/medium/low to manage workload
- Focus effort on high-priority applications
- Don't ignore low priority - they can surprise you!

### Time Filtering

**Filter Options:**
- **7 Days**: Very recent activity (good for weekly reviews)
- **30 Days**: Last month (good for monthly reviews)
- **60 Days**: Last two months (default, good for overall trends)

**Changes When Filtered:**
- Summary statistics recalculate for the time range
- Charts update to show only relevant data
- Better view of recent trends

### Best Practices

✅ **Review analytics weekly** to track progress
✅ **Look for patterns** in successful applications
✅ **Identify bottlenecks** and address them
✅ **Use time filters** to focus on recent activity
✅ **Download charts** for portfolio or progress tracking
✅ **Share with mentors** to get advice on improving your strategy
✅ **Set goals** based on your metrics (e.g., "Increase interview rate to 20%")

---

## 🔍 Advanced Filtering

Find exactly what you need with powerful multi-select filters and date ranges.

### Key Features

- **Multi-Select Status**: Select multiple statuses at once
- **Multi-Select Types**: Filter jobs, scholarships, or both
- **Multi-Select Priority**: High, medium, low combinations
- **Multi-Select Tags**: Filter by one or more tags
- **Date Range Filters**: Deadline and creation date ranges
- **Has Deadline Filter**: Show only apps with/without deadlines
- **Overdue Filter**: Show only overdue applications
- **Search**: Full-text search across title, company, description
- **Persistent Filters**: Filters stay active as you navigate
- **Clear All**: Reset all filters with one click

### Filter Types Explained

#### Search Filter
**What It Does:**
Searches across application title, company name, and description.

**How to Use:**
1. Enter keywords in the search box
2. Press Enter or click Search
3. Results appear instantly

**Examples:**
- Search "Google" to find all Google applications
- Search "software engineer" to find relevant positions
- Search "remote" to find remote opportunities

#### Status Filter (Multi-Select)
**What It Does:**
Show applications in specific stages.

**Available Options:**
- ☐ Draft
- ☐ Submitted
- ☐ In Review
- ☐ Interview
- ☐ Offer
- ☐ Rejected
- ☐ Withdrawn

**How to Use:**
1. Open the **Status** filter section
2. Check one or more boxes
3. Applications matching ANY selected status will appear

**Examples:**
- Select "Interview" + "Offer" to see active opportunities
- Select "Draft" to focus on completing unfinished applications
- Select "Rejected" to review feedback and improve

#### Application Type Filter (Multi-Select)
**What It Does:**
Filter by job or scholarship applications.

**Options:**
- ☐ Job Application
- ☐ Scholarship Application

**How to Use:**
Check the types you want to see. Uncheck to hide.

**Examples:**
- Check only "Job Application" during job search mode
- Check only "Scholarship" when focusing on scholarships
- Check both to see everything

#### Priority Filter (Multi-Select)
**What It Does:**
Filter by priority level.

**Options:**
- ☐ High (🔴 Red flag)
- ☐ Medium (🟡 Yellow flag)
- ☐ Low (🟢 Green flag)

**How to Use:**
Select priority levels to display.

**Examples:**
- Check "High" to focus on top priorities
- Check "Medium" + "Low" to see non-urgent items
- Check all to see everything

#### Tags Filter (Multi-Select)
**What It Does:**
Show applications with specific tags.

**How to Use:**
1. Expand the **Tags** filter section
2. Check one or more tags
3. Applications with ANY of the selected tags appear

**Examples:**
- Select "Remote" to see all remote opportunities
- Select "Dream Company" to see your top choices
- Select "Urgent" + "High Salary" for important, valuable applications

**Combine Tags:**
Selecting multiple tags uses OR logic:
- "Remote" OR "High Salary" = applications that are either remote, high salary, or both

#### Deadline Date Range
**What It Does:**
Filter applications by their deadline dates.

**How to Use:**
1. **Deadline From**: Select start date
2. **Deadline To**: Select end date
3. Applications with deadlines in this range appear

**Examples:**
- This week: Set From = today, To = 7 days from now
- This month: Set From = today, To = end of month
- Q1: Set From = Jan 1, To = Mar 31

**Tip:** Use "Has Deadline" filter to exclude applications without deadlines first.

#### Creation Date Range
**What It Does:**
Filter applications by when they were created.

**How to Use:**
1. **Created From**: Select start date
2. **Created To**: Select end date
3. Applications created in this range appear

**Examples:**
- Last week: Set From = 7 days ago, To = today
- This month: Set From = 1st of month, To = today
- Custom period: Set any date range

**Use Cases:**
- Review recent application activity
- Analyze applications from specific time periods
- Track application volume over time

#### Has Deadline Filter
**What It Does:**
Show only applications with or without deadlines.

**Options:**
- **All**: Show all applications (default)
- **Yes**: Show only applications with deadlines set
- **No**: Show only applications without deadlines

**Examples:**
- Select "Yes" to see applications needing deadline tracking
- Select "No" to find applications missing deadline information

#### Overdue Filter
**What It Does:**
Show only applications that are past their deadline and still in Draft or In Review status.

**How to Use:**
Check the "Show Only Overdue" checkbox

**What It Shows:**
Applications where:
- Deadline has passed (deadline < today)
- Status is "Draft" or "In Review" (not yet submitted or decided)

**Use Cases:**
- Find applications that need immediate attention
- Identify missed opportunities
- Clean up old applications

### Combining Filters

**The Power of Multiple Filters:**
All filters work together using AND logic (except multi-select within each filter uses OR).

**Examples:**

**Find Urgent High-Priority Jobs:**
```
☑ Status: Draft, Submitted
☑ Type: Job Application
☑ Priority: High
☑ Tags: Urgent
```

**Find Remote Opportunities with Deadlines This Month:**
```
☑ Tags: Remote
☑ Has Deadline: Yes
☑ Deadline From: [Start of month]
☑ Deadline To: [End of month]
```

**Review Recent Rejections:**
```
☑ Status: Rejected
☑ Created From: [30 days ago]
☑ Created To: [Today]
```

**Find Dream Companies in Interview Stage:**
```
☑ Status: Interview
☑ Tags: Dream Company
☑ Priority: High
```

### Filter Panel Interface

**Location:**
The filter panel appears on the dashboard page, typically on the left side or as a collapsible panel.

**Expand/Collapse:**
- Click section headers to expand/collapse each filter group
- Keep frequently used filters expanded
- Collapse unused filters to save space

**Active Filter Indicators:**
- Active filters show a badge with count
- Example: "Status (2)" means 2 status filters are active
- Blue highlight on active filter sections

**Clear Filters:**
- **Clear All** button removes all filters at once
- Individual filter sections have "Clear" buttons
- Refresh page to reset filters

### Persistent Filters

**What It Means:**
Filters remain active as you navigate within the dashboard.

**How It Works:**
- Filters are saved in the URL query parameters
- Share the URL to share filtered view
- Bookmark filtered views for quick access

**Example URL:**
```
/tracker/dashboard/?status=interview&status=offer&priority=high&tags=3&tags=5
```

### Performance Tips

**For Large Application Lists:**
- Use search to narrow down before applying other filters
- Combine date ranges with other filters to reduce dataset
- Clear unused filters to improve load times

**Best Practice:**
Start broad, then narrow down:
1. Search for keywords first
2. Filter by status or type
3. Add priority or tag filters
4. Apply date ranges last

---

## ⚡ API Endpoints

New AJAX-powered endpoints for seamless interactions.

### Available Endpoints

#### 1. Note Auto-Save API

**Endpoint:** `POST /tracker/notes/autosave/`

**Purpose:** Auto-save notes without page refresh

**Request Body:**
```json
{
  "note_id": 123,  // Optional: null for new notes
  "title": "My Note Title",
  "content": "<p>Rich text content</p>"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Note saved",
  "note_id": 123,
  "updated_at": "2025-11-06T10:30:00Z"
}
```

**How It's Used:**
- Automatically triggered every 3 seconds when editing notes
- Creates new note if note_id is null
- Updates existing note if note_id is provided

#### 2. Note Toggle Pin API

**Endpoint:** `POST /tracker/notes/<note_id>/toggle-pin/`

**Purpose:** Pin/unpin notes without page refresh

**Response:**
```json
{
  "success": true,
  "is_pinned": true
}
```

**How It's Used:**
- Click the pin icon on any note
- Instantly pins/unpins the note
- No page reload needed

#### 3. Sankey Data API

**Endpoint:** `GET /tracker/analytics/sankey-data/`

**Purpose:** Get application flow data for Sankey diagram

**Response:**
```json
{
  "node": {
    "label": ["Draft", "Submitted", "In Review", ...],
    "color": ["rgba(156, 163, 175, 0.8)", ...],
    "customdata": [10, 25, 15, ...]
  },
  "link": {
    "source": [0, 1, 2, ...],
    "target": [1, 2, 3, ...],
    "value": [5, 10, 3, ...],
    "color": ["rgba(59, 130, 246, 0.4)", ...]
  },
  "total_count": 50
}
```

**How It's Used:**
- Analytics page automatically calls this on load
- Data is cached for 5 minutes to improve performance
- Powers the interactive Sankey diagram

#### 4. Timeline Data API

**Endpoint:** `GET /tracker/analytics/timeline-data/?days=30`

**Purpose:** Get upcoming deadline and interview events

**Query Parameters:**
- `days`: Number of days ahead to show (default: 30, range: 7-90)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Software Engineer",
    "company": "Tech Corp",
    "date": "2025-11-15T09:00:00Z",
    "date_display": "November 15, 2025 at 09:00 AM",
    "type": "interview",
    "status": "interview",
    "status_display": "Interview",
    "priority": "high",
    "priority_display": "High",
    "is_overdue": false,
    "is_today": false,
    "is_this_week": true,
    "days_until": 3
  },
  ...
]
```

**How It's Used:**
- Analytics timeline automatically calls this
- Cached for 5 minutes
- Supports dynamic day filtering

#### 5. Quick Interview Schedule API

**Endpoint:** `POST /tracker/applications/<app_id>/quick-interview/`

**Purpose:** Schedule interview via AJAX modal

**Request Body:**
```json
{
  "interview_type": "video",
  "scheduled_date": "2025-11-15T14:00:00",
  "meeting_link": "https://zoom.us/j/123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Interview scheduled successfully!",
  "interview_id": 42,
  "interview_type": "Video Interview",
  "scheduled_date": "2025-11-15 14:00"
}
```

**How It's Used:**
- Quick interview modal on dashboard
- Instantly schedules interview
- No page reload needed

#### 6. Bulk Archive API

**Endpoint:** `POST /tracker/applications/bulk-archive/`

**Purpose:** Archive multiple applications at once

**Request Body:**
```json
{
  "application_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
  "success": true,
  "message": "5 application(s) archived successfully.",
  "count": 5
}
```

**How It's Used:**
- Bulk actions on dashboard
- Select multiple applications
- Archive all at once

### API Error Handling

All APIs return error responses in this format:

```json
{
  "success": false,
  "message": "Error description"
}
```

**Common HTTP Status Codes:**
- **200 OK**: Success
- **400 Bad Request**: Invalid data
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Using APIs in Custom Scripts

**Example: Auto-save Note**

```javascript
// Auto-save function
async function autoSaveNote(noteId, title, content) {
  const response = await fetch('/tracker/notes/autosave/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      note_id: noteId,
      title: title,
      content: content
    })
  });

  const data = await response.json();

  if (data.success) {
    console.log('Note saved:', data.note_id);
    return data.note_id;
  } else {
    console.error('Save failed:', data.message);
    return null;
  }
}

// Helper to get CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
```

**Example: Bulk Archive**

```javascript
async function bulkArchiveApplications(applicationIds) {
  const response = await fetch('/tracker/applications/bulk-archive/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      application_ids: applicationIds
    })
  });

  const data = await response.json();

  if (data.success) {
    alert(`${data.count} applications archived!`);
    location.reload();
  } else {
    alert('Error: ' + data.message);
  }
}
```

---

## 💡 Tips & Best Practices

### General Workflow

**Daily:**
- [ ] Check overdue filter for urgent action items
- [ ] Review upcoming interviews and deadlines
- [ ] Update application statuses
- [ ] Respond to any notifications

**Weekly:**
- [ ] Review analytics dashboard
- [ ] Clean up draft applications (complete or archive)
- [ ] Follow up on applications in review for 1+ weeks
- [ ] Add notes from any conversations or interviews
- [ ] Plan next week's applications

**Monthly:**
- [ ] Archive completed applications
- [ ] Review and refine tagging system
- [ ] Analyze success metrics in analytics
- [ ] Update your documents with new achievements
- [ ] Review referral relationships and send updates

### Organization Tips

✅ **Use consistent naming** for applications (e.g., "Software Engineer - Google")
✅ **Set deadlines immediately** when you learn about them
✅ **Tag applications as you create them**, not later
✅ **Take notes after every interaction** (interview, email, phone call)
✅ **Update status in real-time** to keep dashboard accurate
✅ **Archive promptly** after definitive outcomes
✅ **Use priority wisely** - not everything can be high priority

### Time Management

**Prioritization Matrix:**

| Deadline | Priority | Action |
|----------|----------|--------|
| This week | High | Do today |
| This week | Medium/Low | Schedule this week |
| This month | High | Schedule this month |
| This month | Medium/Low | Plan for later |
| Later | High | Keep on radar |
| Later | Medium/Low | Archive or delete |

### Data Quality

**Keep Information Complete:**
- Fill in all relevant fields when creating applications
- Add URLs whenever possible (enables AI extraction)
- Upload all relevant documents
- Track referrals immediately
- Note interview details promptly

**Regular Cleanup:**
- Archive old applications monthly
- Delete true duplicates
- Update outdated information
- Remove unused tags
- Consolidate duplicate notes

### Leveraging AI Features

**For Best AI Results:**
1. **Upload complete, formatted documents** (PDF preferred over images)
2. **Provide application URLs** for better question extraction
3. **Review and edit AI responses** - they're starting points, not final answers
4. **Regenerate if needed** - AI can try different approaches
5. **Keep documents updated** - AI uses your latest information

### Success Metrics to Track

**Key Performance Indicators:**
- **Application Volume**: How many you're submitting per week
- **Response Rate**: % of applications getting replies
- **Interview Rate**: % of applications leading to interviews
- **Conversion Rate**: % of interviews leading to offers
- **Time Metrics**: Days from application to interview, interview to offer

**Use Analytics to:**
- Identify which types of applications are most successful
- See where applications are getting stuck
- Optimize your application strategy
- Celebrate progress and wins!

### Troubleshooting

**If filters aren't working:**
- Clear browser cache
- Try the "Clear All" button
- Refresh the page
- Check that you haven't combined contradictory filters

**If auto-save isn't working:**
- Check your internet connection
- Look for error messages in the browser console (F12)
- Try manually saving
- Refresh the page

**If charts aren't loading:**
- Disable browser ad blockers
- Check internet connection
- Try a different browser
- Clear cache and reload

**If referrals/interviews aren't saving:**
- Ensure all required fields are filled
- Check for proper date formats
- Look for validation errors
- Try again with minimal information first

---

## 🎉 Conclusion

These new features are designed to make your job and scholarship application process more organized, efficient, and successful. Take time to explore each feature and integrate them into your workflow.

**Remember:**
- Start small - don't try to use every feature at once
- Build habits - consistent use yields best results
- Customize to your needs - adapt features to your workflow
- Review regularly - weekly analytics reviews help you improve

**Questions or feedback?**
- Open an issue on GitHub
- Check the README for contact information
- Review CLAUDE.md for development details

**Happy job hunting!** 🚀

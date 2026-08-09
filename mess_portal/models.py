from django.db import models


class Menu(models.Model):
    WEEK_CHOICES = [
        ('1&3 Week', 'Week 1 & 3'),
        ('2&4', 'Week 2 & 4'),
    ]
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    SLOT_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('Tea Time', 'Tea Time / Snacks'),
        ('DINNER', 'Dinner'),
    ]

    week = models.CharField(max_length=20, choices=WEEK_CHOICES, default='1&3 Week')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    category = models.CharField(max_length=100, blank=True, default='')
    item = models.CharField(max_length=300)

    class Meta:
        ordering = ['week', 'day']
        verbose_name_plural = 'Menu'

    def __str__(self):
        return '{} · {} · {} — {}'.format(self.day, self.get_slot_display(), self.category, self.item)


class Announcement(models.Model):
    KIND_CHOICES = [
        ('special', 'Special Dinner / Event'),
        ('timing', 'Changed Meal Timings'),
        ('meal', 'Changed Meal / Menu'),
        ('general', 'General'),
    ]
    COLOR_CHOICES = [
        ('#d4183d', 'Red'),
        ('#d97706', 'Amber'),
        ('#2541b2', 'Blue'),
        ('#10b981', 'Green'),
        ('#45347d', 'Purple'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField(max_length=500)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='general')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='#45347d')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # hygiene_pdf=models.FileField(upload_to="hygiene_pdfs/",blank=True,null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Notice(models.Model):
    CATEGORY_CHOICES = [
        ('Rules', 'Rules'),
        ('Timings', 'Timings'),
        ('Hygiene', 'Hygiene'),
        ('Guests', 'Guests'),
        ('Feedback', 'Feedback'),
        ('Other', 'Other'),
    ]
    COLOR_CHOICES = [
        ('#d4183d', 'Red'),
        ('#d97706', 'Amber'),
        ('#2541b2', 'Blue'),
        ('#10b981', 'Green'),
        ('#45347d', 'Purple'),
        ('#8e7db4', 'Lavender'),
    ]

    title = models.CharField(max_length=200)
    text = models.TextField(max_length=500)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Other')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='#45347d')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
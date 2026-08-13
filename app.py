def draw_lollipop(data, title):
        base = alt.Chart(data).encode(x=alt.X('Сектор:N', sort=None, title='Сектор'))
        
        # Линијата одоздола
        rule = base.mark_rule(color='#e45756', strokeWidth=2).encode(y='zero:Q', y2='Вредност:Q')
        
        # Точката на врвот
        points = base.mark_circle(size=120, color='#e45756').encode(y=alt.Y('Вредност:Q', title='Број'))
        
        # Текстуални ознаки (вредности) над точките
        text = base.mark_text(
            align='center',
            baseline='bottom',
            dy=-10  # Растојание од точката
        ).encode(
            y=alt.Y('Вредност:Q'),
            text=alt.Text('Вредност:Q', format='.0f') # Формат на бројот
        )
        
        return (rule + points + text).properties(title=title, height=350)

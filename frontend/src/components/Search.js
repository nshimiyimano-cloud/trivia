import React, { Component } from 'react';

class Search extends Component {
  state = {
    query: '',
  };

  getInfo = (event) => {
    event.preventDefault();
    this.props.submitSearch(this.state.query);
  };

  handleInputChange = () => {
    this.setState({
      query: this.search.value,
    });
  };

  render() {
    return (
      <form onSubmit={this.getInfo} >
        
        <input
          placeholder='Search questions...'
          ref={(input) => (this.search = input)}
          onChange={this.handleInputChange}
          name="serchTerm"
        />
        <input type='submit' value='Submit' className='button' />
      </form>
    );
  }
}

export default Search;


/*

Instead, you can use array_to_string function. Searching on string of other_names will give the same effect

from sqlalchemy import func as F
last_like = "%qq%"
matches = session.query(MyTable).filter(or_(
    MyTable.name.ilike(last_like),
    F.array_to_string(MyTable.other_names, ',').ilike(last_like),
)).all()








  search_term = request.form.get('searchTerm', '')
    if request.method == 'POST':
        search_term = request.form.get('searchTerm', '')
       
    search = search_term.strip()
    #results = Question.query.filter(or_(Question.question.ilike(f'%{search}%'), Question.category.ilike(f'%{search}%'))).all()
    results = Question.query.filter(Question.question.ilike(search)).all()

*/